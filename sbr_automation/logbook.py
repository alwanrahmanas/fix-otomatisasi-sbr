from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Literal

import pandas as pd

Level = Literal["OK", "WARN", "ERROR"]


@dataclass(slots=True)
class LogEvent:
    ts: str
    row_index: int
    level: Level
    stage: str
    note: str
    screenshot: str = ""


@dataclass
class LogBook:
    path: Path
    _events: list[LogEvent] = field(default_factory=list)

    def append(self, event: LogEvent) -> None:
        self._events.append(event)

    def extend(self, events: Iterable[LogEvent]) -> None:
        self._events.extend(events)

    def save(self) -> None:
        if not self._events:
            return
        df = pd.DataFrame([asdict(e) for e in self._events])
        df.to_csv(self.path, index=False)
