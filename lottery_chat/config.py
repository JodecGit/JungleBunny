from __future__ import annotations

GAME_ID = "quebec_49"
DISPLAY_NAME = "Québec 49"
OPERATOR = "Loto-Québec"
MAIN_COUNT = 6
NUMBER_MIN = 1
NUMBER_MAX = 49

# datetime.date.weekday(): Monday=0 … Saturday=5
WEDNESDAY = 2
SATURDAY = 5
DRAW_WEEKDAYS = frozenset({WEDNESDAY, SATURDAY})

WEEKDAY_NAMES_EN = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}

WEEKDAY_NAMES_FR = {
    0: "lundi",
    1: "mardi",
    2: "mercredi",
    3: "jeudi",
    4: "vendredi",
    5: "samedi",
    6: "dimanche",
}

GAME_ALIASES = (
    "québec 49",
    "quebec 49",
    "quebec49",
    "q49",
    "lotto quebec",
    "lotto québec",
    "loto-québec",
    "loto quebec",
    "loto québec",
)

DISCLAIMER_EN = (
    "These are the most frequent numbers in your loaded history, not predicted "
    "winners. Québec 49 draws are random; this set does not improve your odds."
)
DISCLAIMER_FR = (
    "Ce sont les numéros les plus fréquents dans l’historique chargé, pas des "
    "gagnants prédits. Les tirages Québec 49 sont aléatoires; ce jeu n’améliore pas vos chances."
)
