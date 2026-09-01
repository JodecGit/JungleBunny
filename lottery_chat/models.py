from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Draw:
    draw_date: date
    mains: tuple[int, ...]
    bonus: int
    extras: tuple[int, ...] = ()
    source: str = ""
    weekday_mismatch: bool = False

    @property
    def weekday(self) -> int:
        return self.draw_date.weekday()

    def mains_display(self) -> str:
        return " ".join(f"{n:02d}" for n in self.mains)


@dataclass
class LoadResult:
    draws: list[Draw] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    skipped: int = 0
