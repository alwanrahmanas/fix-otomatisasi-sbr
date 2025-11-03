from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Mapping, Optional

from .utils import ensure_directory


BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ensure_directory(BASE_DIR / "artifacts")

DEFAULT_SCREENSHOT_DIR = ensure_directory(ARTIFACTS_DIR / "screenshots")
DEFAULT_CANCEL_SCREENSHOT_DIR = ensure_directory(ARTIFACTS_DIR / "screenshots_cancel")
DEFAULT_LOG_DIR = ensure_directory(ARTIFACTS_DIR / "logs")

DEFAULT_STATUS_ID_MAP: Mapping[str, str] = {
    "Aktif": "kondisi_aktif",
    "Tutup Sementara": "kondisi_tutup_sementara",
    "Belum Beroperasi/Berproduksi": "kondisi_belum_beroperasi_berproduksi",
    "Tutup": "kondisi_tutup",
    "Alih Usaha": "kondisi_alih_usaha",
    "Tidak Ditemukan": "kondisi_tidak_ditemukan",
    "Aktif Pindah": "kondisi_aktif_pindah",
    "Aktif Nonrespon": "kondisi_aktif_nonrespon",
    "Duplikat": "kondisi_duplikat",
    "Salah Kode Wilayah": "kondisi_salah_kode_wilayah",
}


@dataclass(slots=True)
class RuntimeConfig:
    cdp_endpoint: str = "http://localhost:9222"
    sheet_index: int = 0
    pause_after_edit_ms: int = 1000
    pause_after_submit_ms: int = 300
    max_wait_ms: int = 6000
    slow_mode: bool = True
    step_delay_ms: int = 700
    verbose: bool = True
    close_browser_on_exit: bool = False
    status_id_map: Mapping[str, str] = field(default_factory=lambda: DEFAULT_STATUS_ID_MAP)

    screenshot_dir: Path = DEFAULT_SCREENSHOT_DIR
    cancel_screenshot_dir: Path = DEFAULT_CANCEL_SCREENSHOT_DIR
    log_dir: Path = DEFAULT_LOG_DIR


@dataclass(slots=True)
class ExcelSelection:
    path: Path
    sheet_index: int


MatchStrategy = Literal["index", "idsbr", "name"]


@dataclass(slots=True)
class AutofillOptions:
    excel: ExcelSelection
    match_by: MatchStrategy = "index"
    start_row: Optional[int] = None  # 1-indexed from CLI
    end_row: Optional[int] = None  # inclusive
    stop_on_error: bool = False


@dataclass(slots=True)
class CancelOptions:
    excel: ExcelSelection
    match_by: MatchStrategy = "index"
    start_row: Optional[int] = None
    end_row: Optional[int] = None
    stop_on_error: bool = False
