from __future__ import annotations

from collections import Counter
from typing import Iterable

from lottery_chat.config import MAIN_COUNT, NUMBER_MAX, NUMBER_MIN, SATURDAY, WEDNESDAY
from lottery_chat.models import Draw

_WEEKDAY_ALIASES = {
    "wednesday": WEDNESDAY,
    "wed": WEDNESDAY,
    "mercredi": WEDNESDAY,
    "mer": WEDNESDAY,
    "saturday": SATURDAY,
    "sat": SATURDAY,
    "samedi": SATURDAY,
    "sam": SATURDAY,
}


def resolve_weekday(value: int | str | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    key = value.strip().lower()
    if key not in _WEEKDAY_ALIASES:
        raise ValueError(f"Unknown weekday filter: {value}")
    return _WEEKDAY_ALIASES[key]


def filter_by_weekday(draws: Iterable[Draw], weekday: int | str | None) -> list[Draw]:
    draws = list(draws)
    target = resolve_weekday(weekday)
    if target is None:
        return draws
    return [d for d in draws if d.weekday == target]


def main_frequencies(draws: Iterable[Draw]) -> dict[int, int]:
    counts: Counter[int] = Counter()
    for draw in draws:
        counts.update(draw.mains)
    return {n: counts.get(n, 0) for n in range(NUMBER_MIN, NUMBER_MAX + 1)}


def bonus_frequencies(draws: Iterable[Draw]) -> dict[int, int]:
    counts: Counter[int] = Counter(draw.bonus for draw in draws)
    return {n: counts.get(n, 0) for n in range(NUMBER_MIN, NUMBER_MAX + 1)}


def hot_cold(freqs: dict[int, int], n: int = 10) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    ranked = sorted(freqs.items(), key=lambda item: (-item[1], item[0]))
    hot = ranked[:n]
    cold = sorted(ranked, key=lambda item: (item[1], item[0]))[:n]
    return hot, cold


def suggested_ticket(draws: Iterable[Draw], weekday: int | str | None = None) -> dict:
    subset = filter_by_weekday(draws, weekday)
    freqs = main_frequencies(subset)
    ranked = sorted(freqs.items(), key=lambda item: (-item[1], item[0]))
    picks = [number for number, _count in ranked[:MAIN_COUNT]]
    picks.sort()
    label = "all draws" if weekday is None else str(weekday)
    if weekday is not None:
        resolved = resolve_weekday(weekday)
        label = {WEDNESDAY: "Wednesday", SATURDAY: "Saturday"}.get(resolved, label)
    return {
        "numbers": picks,
        "sample_size": len(subset),
        "filter_label": label,
        "frequencies": {n: freqs[n] for n in picks},
    }


def history_rows(draws: Iterable[Draw]) -> list[dict]:
    rows = []
    for draw in draws:
        rows.append(
            {
                "date": draw.draw_date.isoformat(),
                "weekday": draw.draw_date.strftime("%A"),
                "n1": draw.mains[0],
                "n2": draw.mains[1],
                "n3": draw.mains[2],
                "n4": draw.mains[3],
                "n5": draw.mains[4],
                "n6": draw.mains[5],
                "bonus": draw.bonus,
                "mains": draw.mains_display(),
            }
        )
    return rows


def weekday_number_matrix(draws: Iterable[Draw]) -> dict[str, list[int]]:
    labels = ["Wednesday", "Saturday"]
    matrix = {label: [0] * NUMBER_MAX for label in labels}
    for draw in draws:
        label = draw.draw_date.strftime("%A")
        if label not in matrix:
            continue
        for number in draw.mains:
            matrix[label][number - 1] += 1
    return matrix
