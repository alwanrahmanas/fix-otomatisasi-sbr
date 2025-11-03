from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd

from .config import ExcelSelection
from .utils import format_candidates

REQUIRED_COLUMNS_AUTOFILL = ("Status", "Email", "Sumber", "Catatan")


def resolve_excel(path_arg: str | None, search_dir: Path, sheet_index: int) -> ExcelSelection:
    if path_arg:
        path = Path(path_arg).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"File Excel tidak ditemukan: {path}")
        return ExcelSelection(path=path, sheet_index=sheet_index)

    search_locations = [search_dir, search_dir / "data"]
    seen: set[Path] = set()
    candidates: list[Path] = []
    for location in search_locations:
        if not location.exists():
            continue
        for candidate in sorted(location.glob("*.xlsx")):
            resolved = candidate.resolve()
            if resolved not in seen:
                seen.add(resolved)
                candidates.append(resolved)

    if not candidates:
        raise FileNotFoundError(
            "Tidak ditemukan file .xlsx di folder kerja maupun folder 'data'. "
            "Gunakan argumen --excel untuk memilih file secara eksplisit."
        )
    if len(candidates) > 1:
        raise RuntimeError(
            "Ditemukan lebih dari satu file Excel. Pilih salah satu dengan --excel. Kandidat: "
            f"{format_candidates(candidates)}"
        )
    return ExcelSelection(path=candidates[0], sheet_index=sheet_index)


def load_dataframe(selection: ExcelSelection, dtype: str | Sequence[str] | dict | None = str) -> pd.DataFrame:
    return pd.read_excel(selection.path, sheet_name=selection.sheet_index, dtype=dtype)


def ensure_required_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise RuntimeError(f"Kolom wajib belum ada di Excel: {', '.join(missing)}")


def slice_rows(df: pd.DataFrame, start: int | None, end: int | None) -> tuple[int, int]:
    start_idx = 0 if start is None else max(start - 1, 0)
    end_idx = len(df) if end is None else min(end, len(df))
    return start_idx, end_idx
