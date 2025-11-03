from __future__ import annotations

import re
from dataclasses import dataclass

from playwright.async_api import Error as PlaywrightError, Page

from .config import CancelOptions, RuntimeConfig
from .excel_loader import ensure_required_columns, load_dataframe, slice_rows
from .logbook import LogBook, LogEvent
from .playwright_helpers import attach_browser, pick_active_page
from .table_actions import click_edit_by_index, click_edit_by_text
from .utils import ScreenshotResult, describe_exception, note_with_reason, norm_space, take_screenshot, timestamp


REQUIRED_COLUMNS_CANCEL = ("IDSBR", "Nama")


@dataclass(slots=True)
class CancelRowContext:
    table_index: int
    display_index: int
    idsbr: str
    nama: str


async def _log_screenshot(page: Page, label: str, config: RuntimeConfig) -> ScreenshotResult:
    return await take_screenshot(page, config.cancel_screenshot_dir, label)


async def _do_cancel(new_page: Page, config: RuntimeConfig) -> str:
    print("  Membuka tab form...")

    try:
        btn = new_page.locator("xpath=//*[@id='cancel-submit-final']/span")
        if await btn.count() == 0:
            btn = new_page.locator("button:has-text('Cancel Submit'), a:has-text('Cancel Submit')").first
        await btn.wait_for(state="visible", timeout=config.max_wait_ms)
        await btn.scroll_into_view_if_needed(timeout=config.max_wait_ms)
        await btn.click()
        print("    Klik: Cancel Submit")
    except Exception as exc:  # noqa: BLE001
        print(f"    Gagal klik Cancel Submit: {exc}")
        return "ERROR"

    try:
        modal = new_page.locator("div.modal.show, div[role='dialog']")
        with_text = modal.filter(has_text=re.compile("Konfirmasi", re.I)).first
        target = with_text if await with_text.count() > 0 else modal.first
        await target.wait_for(timeout=4000)
        ya_btn = target.locator("button:has-text('Ya, batalkan!'), a:has-text('Ya, batalkan!')").first
        await ya_btn.click(force=True)
        print("    Konfirmasi: Ya, batalkan!")
    except Exception as exc:  # noqa: BLE001
        print(f"    Gagal klik 'Ya, batalkan!': {exc}")
        return "ERROR"

    try:
        for _ in range(20):
            ok_btn = new_page.locator("button:has-text('OK')").first
            if await ok_btn.count() > 0 and await ok_btn.is_visible():
                await ok_btn.click(force=True)
                print("    Success: OK ditekan")
                return "OK"
            await new_page.wait_for_timeout(250)
        print("    Tidak menemukan dialog Success; diasumsikan OK")
        return "OK"
    except Exception as exc:  # noqa: BLE001
        print(f"    Gagal menutup dialog success: {exc}")
        return "ERROR"


async def process_cancel(options: CancelOptions, config: RuntimeConfig) -> None:
    df = load_dataframe(options.excel)
    ensure_required_columns(df, REQUIRED_COLUMNS_CANCEL)

    start_idx, end_idx = slice_rows(df, options.start_row, options.end_row)
    logbook = LogBook(config.log_dir / "log_sbr_cancel.csv")

    ok_rows = 0
    error_rows = 0

    async with attach_browser(config) as (_, context):
        page = pick_active_page(context)

        for i in range(start_idx, end_idx):
            row = df.iloc[i]
            ctx = CancelRowContext(
                table_index=i,
                display_index=i + 1,
                idsbr=norm_space(row.get("IDSBR")),
                nama=norm_space(row.get("Nama")),
            )

            print(f"\n=== Baris {ctx.display_index} :: {ctx.idsbr or ctx.nama} ===")

            clicked = False
            try:
                if options.match_by == "index":
                    clicked = await click_edit_by_index(page, ctx.table_index, timeout=config.max_wait_ms)
                elif options.match_by == "idsbr":
                    clicked = await click_edit_by_text(page, ctx.idsbr, timeout=config.max_wait_ms)
                elif options.match_by == "name":
                    clicked = await click_edit_by_text(page, ctx.nama, timeout=config.max_wait_ms)
            except Exception as exc:  # noqa: BLE001
                shot = await _log_screenshot(page, f"exception_click_edit_{ctx.display_index}", config)
                note = note_with_reason(f"Exception klik Edit: {describe_exception(exc)}", shot)
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
                ya_edit = page.get_by_role("button", name="Ya, edit!")
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
            result = await _do_cancel(new_page, config)

            try:
                await new_page.close()
            except PlaywrightError:
                pass

            await page.bring_to_front()

            logbook.append(LogEvent(timestamp(), ctx.display_index, "OK" if result == "OK" else "ERROR", "CANCEL", result))
            if result == "OK":
                ok_rows += 1
            else:
                error_rows += 1
                if options.stop_on_error:
                    break

    logbook.save()
    print(
        f"\nSelesai Cancel Submit. Baris sukses: {ok_rows} | Baris bermasalah: {error_rows}. "
        f"Log tersimpan di: {logbook.path}"
    )
