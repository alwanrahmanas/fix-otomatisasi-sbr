from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
from playwright.async_api import Page


TIMESTAMP_FMT = "%Y%m%d_%H%M%S"


def timestamp() -> str:
    """Generate a filesystem-friendly timestamp."""
    return datetime.now().strftime(TIMESTAMP_FMT)


def norm_space(value: object) -> str:
    """Normalize whitespace and coerce NaN/None to empty string."""
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    # pandas may give numpy scalars; cast to string first
    return re.sub(r"\s+", " ", str(value)).strip()


def norm_phone(value: object) -> str:
    """Keep only digits of telephone input."""
    digits = re.findall(r"\d", norm_space(value))
    return "".join(digits)


def norm_float(value: object) -> str:
    """Extract first float-compatible token from text."""
    text = norm_space(value).replace(",", ".")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return match.group(0) if match else ""


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


@dataclass(slots=True)
class ScreenshotResult:
    path: Optional[Path]
    reason: str | None = None


async def take_screenshot(page: Page, dest_dir: Path, label: str) -> ScreenshotResult:
    """Capture screenshot with sanitized filename."""
    safe_label = re.sub(r"[^a-zA-Z0-9_-]+", "-", label).strip("-") or "capture"
    filename = f"{timestamp()}_{safe_label[:40]}.png"
    target = ensure_directory(dest_dir) / filename
    try:
        await page.screenshot(path=str(target), full_page=True)
        return ScreenshotResult(target)
    except Exception as exc:  # noqa: BLE001
        return ScreenshotResult(None, reason=str(exc))


def format_candidates(files: Iterable[Path]) -> str:
    return ", ".join(sorted(str(p) for p in files))


def describe_exception(exc: Exception) -> str:
    return f"{exc.__class__.__name__}: {exc}"


def note_with_reason(note: str, shot: ScreenshotResult) -> str:
    if shot.path or not shot.reason:
        return note
    return f"{note} (screenshot-error: {shot.reason})"
