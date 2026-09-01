from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

from lottery_chat.config import DRAW_WEEKDAYS, MAIN_COUNT, NUMBER_MAX, NUMBER_MIN
from lottery_chat.models import Draw, LoadResult

_ENCODINGS = ("utf-8-sig", "utf-8", "cp1252")
_YMD = re.compile(r"\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b")
_DMY = re.compile(r"\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b")
_INTS = re.compile(r"\d+")
_HEADER = re.compile(r"date|bonus|num[eé]ro|draw|tirage", re.IGNORECASE)


def load_path(path: str | Path) -> LoadResult:
    path = Path(path)
    raw = path.read_bytes()
    return load_bytes(raw, source=str(path))


def load_bytes(data: bytes, source: str = "") -> LoadResult:
    text = _decode(data)
    return load_text(text, source=source)


def load_text(text: str, source: str = "") -> LoadResult:
    result = LoadResult()
    by_date: dict[date, Draw] = {}
    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parsed = _parse_line(line, source=source)
        if parsed is None:
            looks_like_header = bool(_HEADER.search(line)) and _extract_date(line)[0] is None
            if looks_like_header:
                continue
            result.skipped += 1
            result.errors.append(f"{source or 'input'}:{line_no}: could not parse: {line}")
            continue
        draw, warning = parsed
        by_date[draw.draw_date] = draw
        if warning:
            result.warnings.append(f"{source or 'input'}:{line_no}: {warning}")
    result.draws = sorted(by_date.values(), key=lambda d: d.draw_date)
    return result


def merge_results(*results: LoadResult) -> LoadResult:
    merged = LoadResult()
    by_date: dict[date, Draw] = {}
    for res in results:
        merged.errors.extend(res.errors)
        merged.warnings.extend(res.warnings)
        merged.skipped += res.skipped
        for draw in res.draws:
            by_date[draw.draw_date] = draw
    merged.draws = sorted(by_date.values(), key=lambda d: d.draw_date)
    return merged


def _decode(data: bytes) -> str:
    for encoding in _ENCODINGS:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _parse_line(line: str, source: str) -> tuple[Draw, str | None] | None:
    draw_date, remainder = _extract_date(line)
    if draw_date is None:
        return None
    numbers = _ints_in_range(remainder)
    if len(numbers) < MAIN_COUNT + 1:
        return None
    mains = tuple(numbers[:MAIN_COUNT])
    if len(set(mains)) != MAIN_COUNT:
        return None
    rest = numbers[MAIN_COUNT:]
    bonus = rest[0]
    if bonus in mains:
        return None
    extras = tuple(n for n in rest[1:] if n not in mains and n != bonus)
    mismatch = draw_date.weekday() not in DRAW_WEEKDAYS
    warning = None
    if mismatch:
        warning = (
            f"{draw_date.isoformat()} is {draw_date.strftime('%A')}, "
            "not a usual Québec 49 draw day (Wednesday/Saturday)"
        )
    draw = Draw(
        draw_date=draw_date,
        mains=mains,
        bonus=bonus,
        extras=extras,
        source=source,
        weekday_mismatch=mismatch,
    )
    return draw, warning


def _extract_date(line: str) -> tuple[date | None, str]:
    match = _YMD.search(line)
    if match:
        year, month, day = (int(g) for g in match.groups())
        parsed = _safe_date(year, month, day)
        if parsed:
            remainder = line[: match.start()] + " " + line[match.end() :]
            return parsed, remainder
    match = _DMY.search(line)
    if match:
        day, month, year = (int(g) for g in match.groups())
        parsed = _safe_date(year, month, day)
        if parsed:
            remainder = line[: match.start()] + " " + line[match.end() :]
            return parsed, remainder
    return None, line


def _safe_date(year: int, month: int, day: int) -> date | None:
    try:
        return datetime(year, month, day).date()
    except ValueError:
        return None


def _ints_in_range(text: str) -> list[int]:
    values: list[int] = []
    seen_in_ticket: set[int] = set()
    for token in _INTS.findall(text):
        number = int(token)
        if NUMBER_MIN <= number <= NUMBER_MAX and number not in seen_in_ticket:
            values.append(number)
            seen_in_ticket.add(number)
    return values
