from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from sbr_automation.autofill import process_autofill
from sbr_automation.config import AutofillOptions, ExcelSelection, MatchStrategy, RuntimeConfig
from sbr_automation.excel_loader import resolve_excel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SBR Autofill (Chrome attach via CDP)")
    parser.add_argument("--excel", help="Path ke file Excel (jika tidak diisi akan auto-scan folder kerja)")
    parser.add_argument("--sheet", type=int, default=0, help="Index sheet Excel (default: 0)")
    parser.add_argument("--match-by", choices=["index", "idsbr", "name"], default="index", help="Metode mencari tombol Edit")
    parser.add_argument("--start", type=int, help="Mulai dari baris ke- (1-indexed)")
    parser.add_argument("--end", type=int, help="Sampai baris ke- (inklusif)")
    parser.add_argument("--stop-on-error", action="store_true", help="Berhenti saat menemukan error pertama")
    parser.add_argument(
        "--cdp-endpoint",
        default="http://localhost:9222",
        help="Endpoint CDP Chrome (default: http://localhost:9222)",
    )
    parser.add_argument("--no-slow-mode", action="store_true", help="Menonaktifkan jeda antar langkah")
    parser.add_argument("--step-delay", type=int, default=700, help="Lama jeda slow mode (ms)")
    parser.add_argument("--pause-after-edit", type=int, default=1000, help="Jeda setelah klik Edit (ms)")
    parser.add_argument("--pause-after-submit", type=int, default=300, help="Jeda setelah klik Submit (ms)")
    parser.add_argument("--max-wait", type=int, default=6000, help="Timeout tunggu elemen/tab (ms)")
    return parser.parse_args()


def build_options(args: argparse.Namespace, working_dir: Path) -> tuple[AutofillOptions, RuntimeConfig]:
    excel_selection: ExcelSelection = resolve_excel(args.excel, working_dir, args.sheet)
    options = AutofillOptions(
        excel=excel_selection,
        match_by=args.match_by,
        start_row=args.start,
        end_row=args.end,
        stop_on_error=args.stop_on_error,
    )

    config = RuntimeConfig(
        cdp_endpoint=args.cdp_endpoint,
        sheet_index=args.sheet,
        pause_after_edit_ms=args.pause_after_edit,
        pause_after_submit_ms=args.pause_after_submit,
        max_wait_ms=args.max_wait,
        slow_mode=not args.no_slow_mode,
        step_delay_ms=args.step_delay,
    )
    return options, config


def main() -> None:
    args = parse_args()
    options, config = build_options(args, Path.cwd())
    asyncio.run(process_autofill(options, config))


if __name__ == "__main__":
    main()
