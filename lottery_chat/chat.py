from __future__ import annotations

from dataclasses import dataclass

from lottery_chat.analyzer import hot_cold, main_frequencies, suggested_ticket
from lottery_chat.config import DISCLAIMER_EN, DISCLAIMER_FR, DISPLAY_NAME, GAME_ALIASES
from lottery_chat.models import Draw


@dataclass(frozen=True)
class ChatReply:
    text: str
    show_history: bool = False
    show_graphs: bool = False


def reply(message: str, draws: list[Draw]) -> ChatReply:
    text = message.strip()
    if not text:
        return ChatReply("Ask about best numbers, Wednesday, Saturday, history, or graphs.")
    french = _looks_french(text)
    if not draws:
        if french:
            return ChatReply(
                "Aucun tirage chargé. Ajoutez un fichier .txt ou .csv dans la barre latérale."
            )
        return ChatReply("No draws loaded yet. Upload a .txt or .csv file in the sidebar.")

    weekday = _weekday_intent(text)
    wants_history = _has_any(
        text,
        ("history", "historique", "all draws", "tous les tirages"),
    )
    wants_graphs = _has_any(
        text,
        ("graph", "chart", "hot", "cold", "graphique", "frequen", "fréquen"),
    )
    wants_best = _has_any(
        text,
        (
            "best",
            "play",
            "ticket",
            "suggest",
            "meilleur",
            "jouer",
        ),
    ) or weekday is not None
    wants_numbers = _has_any(
        text,
        ("numéro", "numero", "numbers", "numeros", "numéros"),
    )

    if wants_history:
        return ChatReply(
            _history_blurb(draws, french),
            show_history=True,
        )
    if wants_graphs:
        return ChatReply(
            _graphs_blurb(draws, french),
            show_graphs=True,
        )

    if wants_best or wants_numbers:
        suggestion = suggested_ticket(draws, weekday)
        return ChatReply(_best_blurb(suggestion, french))

    if french:
        return ChatReply(
            "Je peux indiquer les numéros les plus fréquents (mercredi, samedi ou tous), "
            "l’historique, ou les graphiques. Exemple : « meilleurs numéros samedi »."
        )
    return ChatReply(
        f"I can show the most frequent {DISPLAY_NAME} numbers (Wednesday, Saturday, or all), "
        "full history, or graphs. Try: “best numbers for Saturday”."
    )


def _best_blurb(suggestion: dict, french: bool) -> str:
    numbers = " ".join(f"{n:02d}" for n in suggestion["numbers"])
    sample = suggestion["sample_size"]
    label = suggestion["filter_label"]
    if french:
        label_fr = {"Wednesday": "mercredi", "Saturday": "samedi", "all draws": "tous les tirages"}.get(
            label, label
        )
        freq = ", ".join(f"{n:02d}×{c}" for n, c in suggestion["frequencies"].items())
        return (
            f"{DISPLAY_NAME} — sélection basée sur la fréquence ({label_fr}, {sample} tirage(s)):\n"
            f"**{numbers}**\n"
            f"Apparitions: {freq}\n\n"
            f"{DISCLAIMER_FR}"
        )
    freq = ", ".join(f"{n:02d}×{c}" for n, c in suggestion["frequencies"].items())
    return (
        f"{DISPLAY_NAME} — frequency-based pick ({label}, {sample} draw(s)):\n"
        f"**{numbers}**\n"
        f"Appearances: {freq}\n\n"
        f"{DISCLAIMER_EN}"
    )


def _history_blurb(draws: list[Draw], french: bool) -> str:
    first = draws[0].draw_date.isoformat()
    last = draws[-1].draw_date.isoformat()
    if french:
        return (
            f"{len(draws)} tirages {DISPLAY_NAME} du {first} au {last}. "
            "Ouvrez l’onglet Historique pour le tableau complet."
        )
    return (
        f"{len(draws)} {DISPLAY_NAME} draws from {first} to {last}. "
        "Open the History tab for the full table."
    )


def _graphs_blurb(draws: list[Draw], french: bool) -> str:
    freqs = main_frequencies(draws)
    hot, _cold = hot_cold(freqs, n=10)
    top = ", ".join(f"{n:02d} ({c})" for n, c in hot)
    if french:
        return (
            f"Top 10 des numéros principaux ({len(draws)} tirages): {top}. "
            "Voir l’onglet Graphiques pour les barres mercredi/samedi, le bonus et le heatmap."
        )
    return (
        f"Top 10 main numbers ({len(draws)} draws): {top}. "
        "See the Graphs tab for Wednesday/Saturday bars, bonus, and heatmap."
    )


def _weekday_intent(text: str) -> str | None:
    lowered = _normalize(text)
    if any(word in lowered for word in ("wednesday", "wed", "mercredi")):
        return "wednesday"
    if any(word in lowered for word in ("saturday", "sat", "samedi")):
        return "saturday"
    return None


def _looks_french(text: str) -> bool:
    lowered = _normalize(text)
    markers = (
        "meilleur",
        "numéro",
        "numero",
        "mercredi",
        "samedi",
        "historique",
        "graphique",
        "tirage",
        "jouer",
        "fréquence",
        "frequence",
        "québec",
        "quebec",
    )
    return any(m in lowered for m in markers) and not any(
        e in lowered for e in ("best", "wednesday", "saturday", "history", "graph", "what to play")
    )


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = _normalize(text)
    return any(needle in lowered for needle in needles)


def _normalize(text: str) -> str:
    lowered = text.lower()
    for alias in GAME_ALIASES:
        lowered = lowered.replace(alias, " ")
    return " ".join(lowered.split())
