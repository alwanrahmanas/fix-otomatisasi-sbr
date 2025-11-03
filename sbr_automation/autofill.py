from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from playwright.async_api import Error as PlaywrightError, Locator, Page

from .config import AutofillOptions, RuntimeConfig
from .excel_loader import (
    REQUIRED_COLUMNS_AUTOFILL,
    ensure_required_columns,
    load_dataframe,
    slice_rows,
)
from .logbook import LogBook, LogEvent
from .playwright_helpers import attach_browser, pick_active_page, slow_pause
from .table_actions import click_edit_by_index, click_edit_by_text
from .utils import (
    ScreenshotResult,
    describe_exception,
    note_with_reason,
    norm_float,
    norm_phone,
    norm_space,
    take_screenshot,
    timestamp,
)


@dataclass(slots=True)
class RowContext:
    table_index: int
    display_index: int
    nama: str
    status: str
    phone: str
    email: str
    latitude: str
    longitude: str
    sumber: str
    catatan: str


PHONE_COLUMN_CANDIDATES = (
    "Nomor Telepon",
    "nomor_telepon",
    "No Telepon",
    "No. Telepon",
    "Telepon",
    "Telepon/HP",
    "Phone",
)

STATUS_NORMALIZATION = {
    "aktif nonrespons": "Aktif Nonrespon",
    "belum berproduksi": "Belum Beroperasi/Berproduksi",
}


def _select_phone_value(df_row) -> object:
    columns = getattr(df_row, "index", ())
    for column in PHONE_COLUMN_CANDIDATES:
        if column in columns:
            value = df_row.get(column)
            if norm_space(value):
                return value
    for column in PHONE_COLUMN_CANDIDATES:
        if column in columns:
            return df_row.get(column)
    return df_row.get("Nomor Telepon")


def _normalize_status(status: str) -> str:
    if not status:
        return ""
    return STATUS_NORMALIZATION.get(status.lower(), status)


async def _log_screenshot(
    page: Page,
    label: str,
    config: RuntimeConfig,
    *,
    for_cancel: bool = False,
) -> ScreenshotResult:
    directory = config.cancel_screenshot_dir if for_cancel else config.screenshot_dir
    return await take_screenshot(page, directory, label)


async def _is_locked_page(page: Page) -> bool:
    patterns = [
        re.compile("tidak bisa melakukan edit", re.I),
        re.compile("sedang diedit oleh user lain", re.I),
    ]
    for pattern in patterns:
        try:
            locator = page.get_by_text(pattern)
            await locator.wait_for(state="visible", timeout=1500)
            return True
        except Exception:  # noqa: BLE001
            continue

    try:
        back_btn = page.get_by_role("button", name=re.compile("Back to Home", re.I))
        await back_btn.wait_for(state="visible", timeout=1500)
        return True
    except Exception:  # noqa: BLE001
        pass
    return False


async def _apply_status(page: Page, ctx: RowContext, config: RuntimeConfig) -> None:
    if not ctx.status:
        return

    radio_id = config.status_id_map.get(ctx.status)
    if radio_id:
        radio = page.locator(f"#{radio_id}")
        try:
            await radio.wait_for(state="attached", timeout=2000)
            try:
                await radio.check()
            except Exception:
                await radio.click(force=True)
            print(f"    Status usaha diatur ke: {ctx.status}")
        except Exception as exc:  # noqa: BLE001
            print(f"    Gagal set status '{ctx.status}': {describe_exception(exc)}")
    else:
        lbl = page.locator("label").filter(has_text=re.compile(re.escape(ctx.status), re.I)).first
        try:
            await lbl.wait_for(state="visible", timeout=2000)
            target_id = await lbl.get_attribute("for")
            if target_id:
                await page.locator(f"#{target_id}").check()
            else:
                await lbl.click(force=True)
            print(f"    Status usaha diisi melalui label fallback: {ctx.status}")
        except Exception as exc:  # noqa: BLE001
            print(f"    Gagal menemukan label status '{ctx.status}': {describe_exception(exc)}")

    await slow_pause(page, config)


async def _focus_identitas_section(page: Page) -> None:
    try:
        ident_section = page.locator(
            "xpath=//*[self::h4 or self::h5][contains(., 'IDENTITAS USAHA/PERUSAHAAN')]"
            "/ancestor::*[contains(@class,'card') or contains(@class,'section')][1]"
        )
        if await ident_section.count() > 0:
            await ident_section.scroll_into_view_if_needed()
    except Exception as exc:  # noqa: BLE001
        print(f"    Gagal memfokus bagian Identitas: {describe_exception(exc)}")


async def _fill_phone(page: Page, phone: str) -> None:
    try:
        tel_input = (
            page.get_by_placeholder(re.compile(r"^Nomor\s*Telepon$", re.I))
            .or_(page.locator("input#nomor_telepon, input[name='nomor_telepon'], input[name='no_telp'], input[name='telepon']"))
        ).first
        await tel_input.wait_for(state="visible", timeout=1500)
        if phone:
            await tel_input.fill("")
            await tel_input.fill(phone)
            print(f"    Nomor telepon diisi: {phone}")
        else:
            print("    Nomor telepon dilewati (kosong).")
    except Exception as exc:  # noqa: BLE001
        print(f"    Pengisian nomor telepon bermasalah: {describe_exception(exc)}")


async def _fill_email(page: Page, ctx: RowContext) -> None:
    try:
        cb_email = page.locator("#check-email").first
        if await cb_email.count() > 0:
            await cb_email.wait_for(state="attached", timeout=500)

        email_input = (
            page.locator("input#email, input[name='email'], input[type='email']")
            .or_(page.get_by_placeholder(re.compile(r"^email$", re.I)))
        ).first

        web_state = await page.evaluate(
            """
            () => {
                const inp = document.querySelector('input#email, input[name="email"], input[type="email"]');
                return inp ? (inp.value || '').trim() : '';
            }
            """
        )
        web_value = web_state.strip()

        if ctx.email:
            try:
                await email_input.wait_for(state="visible", timeout=400)
                await email_input.fill("")
                await email_input.fill(ctx.email)
                print(f"    Email diisi: {ctx.email}")
            except Exception as exc:  # noqa: BLE001
                print(f"    Gagal mengisi email: {describe_exception(exc)}")
        elif web_value:
            print(f"    Email sudah ada di web, dibiarkan: {web_value}")
        else:
            try:
                await page.evaluate(
                    """
                    () => {
                        const cb = document.querySelector('#check-email');
                        const inp = document.querySelector('input#email, input[name="email"], input[type="email"]');
                        if (cb) {
                            cb.checked = false;
                            cb.dispatchEvent(new Event('input', { bubbles: true }));
                            cb.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                        if (inp) {
                            inp.value = '';
                            inp.dispatchEvent(new Event('input', { bubbles: true }));
                            inp.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }
                    """
                )
                print("    Toggle email dimatikan (kosong).")
            except Exception as exc:  # noqa: BLE001
                print(f"    Gagal mematikan toggle email: {describe_exception(exc)}")
    except Exception as exc:  # noqa: BLE001
        print(f"    Pengelolaan email bermasalah: {describe_exception(exc)}")


async def _fill_coordinates(page: Page, ctx: RowContext) -> None:
    if ctx.latitude:
        try:
            lat_input = (
                page.locator("input#latitude, input[name='latitude']")
                .or_(page.get_by_placeholder(re.compile(r"^latitude", re.I)))
            ).first
            await lat_input.wait_for(state="visible", timeout=1500)
            await lat_input.fill("")
            await lat_input.fill(ctx.latitude)
            print(f"    Latitude diisi: {ctx.latitude}")
        except Exception as exc:  # noqa: BLE001
            print(f"    Gagal mengisi latitude: {describe_exception(exc)}")
    else:
        print("    Latitude dilewati.")

    if ctx.longitude:
        try:
            lon_input = (
                page.locator("input#longitude, input[name='longitude']")
                .or_(page.get_by_placeholder(re.compile(r"^longitude", re.I)))
            ).first
            await lon_input.wait_for(state="visible", timeout=1500)
            await lon_input.fill("")
            await lon_input.fill(ctx.longitude)
            print(f"    Longitude diisi: {ctx.longitude}")
        except Exception as exc:  # noqa: BLE001
            print(f"    Gagal mengisi longitude: {describe_exception(exc)}")
    else:
        print("    Longitude dilewati.")


async def _fill_identitas_section(page: Page, ctx: RowContext) -> None:
    await _focus_identitas_section(page)
    await _fill_phone(page, ctx.phone)
    await _fill_email(page, ctx)
    await _fill_coordinates(page, ctx)


async def _fill_additional_fields(page: Page, ctx: RowContext, config: RuntimeConfig) -> None:
    if ctx.sumber:
        try:
            await page.get_by_placeholder(re.compile("Sumber Profiling", re.I)).fill(ctx.sumber)
            print(f"    Sumber Profiling diisi: {ctx.sumber}")
        except Exception as exc:  # noqa: BLE001
            print(f"    Field Sumber Profiling tidak ditemukan: {describe_exception(exc)}")
        await slow_pause(page, config)

    if ctx.catatan:
        try:
            await page.wait_for_selector("#catatan_profiling", state="visible", timeout=3000)
            await page.fill("#catatan_profiling", ctx.catatan)
            await page.evaluate(
                """
                () => {
                    const el = document.querySelector('#catatan_profiling');
                    if (el) {
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
                """
            )
            print(f"    Catatan diisi ({len(ctx.catatan)} karakter).")
        except Exception as exc:  # noqa: BLE001
            print(f"    Gagal mengisi catatan: {describe_exception(exc)}")
        await slow_pause(page, config)


async def _fill_form(page: Page, ctx: RowContext, config: RuntimeConfig) -> None:
    print("  Mengisi form...")
    await _apply_status(page, ctx, config)
    await _fill_identitas_section(page, ctx)
    await _fill_additional_fields(page, ctx, config)
    print("  Form selesai diisi.")


async def _submit_and_handle(page: Page, ctx: RowContext, config: RuntimeConfig) -> str:
    btn_role = page.get_by_role("button", name=re.compile("Submit Final", re.I))
    btn_text = page.locator("text=Submit Final").first

    async def try_click(locator: Locator) -> bool:
        try:
            if await locator.is_visible(timeout=800):
                await locator.click()
                return True
        except Exception:
            return False
        return False

    if not (await try_click(btn_role) or await try_click(btn_text)):
        return "NO_SUBMIT_BUTTON"

    await page.wait_for_timeout(config.pause_after_submit_ms)

    try:
        err = page.get_by_text(re.compile("Masih terdapat isian yang harus diperbaiki", re.I))
        await err.wait_for(state="visible", timeout=1000)
        ok = page.get_by_role("button", name=re.compile("^OK$", re.I))
        if await ok.is_visible():
            await ok.click()
        return "ERROR_FILL"
    except Exception:
        pass

    try:
        kons = page.get_by_text(re.compile("Cek Konsistensi", re.I))
        await kons.wait_for(state="visible", timeout=800)
        ign = page.get_by_role("button", name=re.compile("^Ignore$", re.I))
        if await ign.is_visible():
            await ign.click(force=True)
            await page.wait_for_timeout(250)
    except Exception:
        pass

    clicked_confirm = False
    for _ in range(10):
        ya = page.locator("div.modal.show, div[role='dialog']").locator(
            "button:has-text('Ya, Submit'), a:has-text('Ya, Submit'), button:has-text('Ya, Submit!'), a:has-text('Ya, Submit!')"
        ).first
        if await ya.count() > 0 and await ya.is_visible():
            try:
                await ya.click(force=True)
            except Exception:
                await page.evaluate(
                    """
                    () => {
                        const modal = document.querySelector('.modal.show,[role="dialog"]');
                        if (!modal) return;
                        const btn = [...modal.querySelectorAll('button,a')].find(el =>
                            /ya\\s*,?\\s*submit!?/i.test((el.textContent || '').trim())
                        );
                        if (btn) btn.click();
                    }
                    """
                )
            clicked_confirm = True
            break
        await page.wait_for_timeout(250)

    async def submit_still_visible() -> bool:
        try:
            if await btn_role.is_visible(timeout=200):
                return True
        except Exception:
            pass
        try:
            if await btn_text.is_visible(timeout=200):
                return True
        except Exception:
            pass
        return False

    success_seen = False
    for _ in range(16):
        try:
            sm = page.get_by_text(re.compile("Success|Berhasil submit data final", re.I))
            if await sm.is_visible(timeout=120):
                okb = page.get_by_role("button", name=re.compile("^OK$", re.I))
                if await okb.is_visible():
                    await okb.click(force=True)
                    await page.wait_for_timeout(150)
                success_seen = True
                break
        except Exception:
            pass

        toast = page.locator(".toast, .alert-success, .swal2-popup").first
        try:
            if await toast.is_visible(timeout=120):
                success_seen = True
                break
        except Exception:
            pass

        if not await submit_still_visible():
            success_seen = True
            break

        await page.wait_for_timeout(200)

    if success_seen:
        return "OK"
    if clicked_confirm:
        return "NO_SUCCESS_SIGNAL"
    return "NO_CONFIRM"


def _context_from_row(df_row, table_index: int, display_index: int) -> RowContext:
    return RowContext(
        table_index=table_index,
        display_index=display_index,
        nama=norm_space(df_row.get("Nama")),
        status=_normalize_status(norm_space(df_row.get("Status"))),
        phone=norm_phone(_select_phone_value(df_row)),
        email=norm_space(df_row.get("Email")),
        latitude=norm_float(df_row.get("Latitude")),
        longitude=norm_float(df_row.get("Longitude")),
        sumber=norm_space(df_row.get("Sumber")),
        catatan=norm_space(df_row.get("Catatan")),
    )


async def process_autofill(options: AutofillOptions, config: RuntimeConfig) -> None:
    df = load_dataframe(options.excel)
    ensure_required_columns(df, REQUIRED_COLUMNS_AUTOFILL)

    start_idx, end_idx = slice_rows(df, options.start_row, options.end_row)
    logbook = LogBook(config.log_dir / "log_sbr_autofill.csv")

    ok_rows = 0
    skipped_rows = 0
    error_rows = 0

    async with attach_browser(config) as (_, context):
        page = pick_active_page(context)

        for i in range(start_idx, end_idx):
            row = df.iloc[i]
            ctx = _context_from_row(row, i, i + 1)

            print(f"\n=== Baris {ctx.display_index} :: {ctx.nama or '(tanpa nama)'} :: Status = {ctx.status or '-'} ===")

            clicked = False
            try:
                if options.match_by == "index":
                    clicked = await click_edit_by_index(page, ctx.table_index, timeout=config.max_wait_ms)
                elif options.match_by == "idsbr":
                    clicked = await click_edit_by_text(page, norm_space(row.get("IDSBR")), timeout=config.max_wait_ms)
                elif options.match_by == "name":
                    clicked = await click_edit_by_text(page, ctx.nama, timeout=config.max_wait_ms)
            except Exception as exc:  # noqa: BLE001
                shot = await _log_screenshot(page, f"exception_click_edit_{ctx.display_index}", config)
                note = note_with_reason(f"CLICK_EDIT_EXCEPTION: {describe_exception(exc)}", shot)
                logbook.append(LogEvent(timestamp(), ctx.display_index, "ERROR", "CLICK_EDIT", note, shot.path or ""))
                error_rows += 1
                if options.stop_on_error:
                    break
                continue

            if not clicked:
                shot = await _log_screenshot(page, f"gagal_click_edit_{ctx.display_index}", config)
                note = note_with_reason("Tombol Edit tidak ditemukan", shot)
                logbook.append(LogEvent(timestamp(), ctx.display_index, "ERROR", "CLICK_EDIT", note, shot.path or ""))
                error_rows += 1
                if options.stop_on_error:
                    break
                continue

            try:
                ya_edit = page.get_by_role("button", name=re.compile(r"Ya,\s*edit!?$", re.I))
                if await ya_edit.count() > 0:
                    await ya_edit.click()
            except PlaywrightError:
                pass

            await page.wait_for_timeout(config.pause_after_edit_ms)

            try:
                new_page = await context.wait_for_event("page", timeout=config.max_wait_ms)
            except PlaywrightError as exc:
                shot = await _log_screenshot(page, f"no_new_tab_{ctx.display_index}", config)
                note = note_with_reason(f"Tidak ada tab form: {describe_exception(exc)}", shot)
                logbook.append(LogEvent(timestamp(), ctx.display_index, "ERROR", "OPEN_TAB", note, shot.path or ""))
                error_rows += 1
                if options.stop_on_error:
                    break
                continue

            await new_page.bring_to_front()

            if await _is_locked_page(new_page):
                shot = await _log_screenshot(new_page, f"locked_{ctx.display_index}", config)
                note = note_with_reason(
                    "FORM_LOCKED: Usaha sedang diedit oleh pengguna lain. Tutup tab sebelum lanjut.", shot
                )
                print("  Lock terdeteksi: usaha sedang dibuka oleh pengguna lain. Melewati baris.")
                logbook.append(LogEvent(timestamp(), ctx.display_index, "WARN", "ACCESS", note, shot.path or ""))
                try:
                    await new_page.close()
                except PlaywrightError:
                    pass
                await page.bring_to_front()
                skipped_rows += 1
                continue

            try:
                await _fill_form(new_page, ctx, config)
                logbook.append(LogEvent(timestamp(), ctx.display_index, "OK", "FILL", "Form terisi"))
            except Exception as exc:  # noqa: BLE001
                shot = await _log_screenshot(new_page, f"exception_fill_form_{ctx.display_index}", config)
                note = note_with_reason(f"Exception isi form: {describe_exception(exc)}", shot)
                logbook.append(LogEvent(timestamp(), ctx.display_index, "ERROR", "FILL", note, shot.path or ""))
                error_rows += 1
                try:
                    await new_page.close()
                except PlaywrightError:
                    pass
                if options.stop_on_error:
                    break
                else:
                    await page.bring_to_front()
                    continue

            try:
                result = await _submit_and_handle(new_page, ctx, config)
                if result != "OK":
                    shot = await _log_screenshot(new_page, f"submit_issue_{ctx.display_index}_{result}", config)
                    note = note_with_reason(result, shot)
                    logbook.append(LogEvent(timestamp(), ctx.display_index, "ERROR", "SUBMIT", note, shot.path or ""))
                    error_rows += 1
                    try:
                        await new_page.close()
                    except PlaywrightError:
                        pass
                    await page.bring_to_front()
                    if options.stop_on_error:
                        break
                    continue
                else:
                    logbook.append(LogEvent(timestamp(), ctx.display_index, "OK", "SUBMIT", "Submit final sukses"))
            except Exception as exc:  # noqa: BLE001
                shot = await _log_screenshot(new_page, f"exception_submit_{ctx.display_index}", config)
                note = note_with_reason(f"EXCEPTION: {describe_exception(exc)}", shot)
                logbook.append(LogEvent(timestamp(), ctx.display_index, "ERROR", "SUBMIT", note, shot.path or ""))
                error_rows += 1
                if options.stop_on_error:
                    try:
                        await new_page.close()
                    except PlaywrightError:
                        pass
                    break
                else:
                    try:
                        await new_page.close()
                    except PlaywrightError:
                        pass
                    await page.bring_to_front()
                    continue

            try:
                await new_page.close()
            except PlaywrightError:
                pass

            await page.bring_to_front()
            await page.wait_for_timeout(800)
            logbook.append(LogEvent(timestamp(), ctx.display_index, "OK", "ROW_DONE", "Baris selesai diproses"))
            ok_rows += 1

    logbook.save()
    print(
        f"\nSelesai. Baris sukses: {ok_rows} | Baris bermasalah: {error_rows} | Baris dilewati: {skipped_rows}. "
        f"Log tersimpan di: {logbook.path}"
    )
