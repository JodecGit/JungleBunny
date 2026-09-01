"""Québec 49 analysis package. Streamlit UI should import from here only."""

from lottery_chat.analyzer import (
    bonus_frequencies,
    filter_by_weekday,
    history_rows,
    hot_cold,
    main_frequencies,
    suggested_ticket,
    weekday_number_matrix,
)
from lottery_chat.chat import reply
from lottery_chat.charts import (
    bonus_frequency_figure,
    heatmap_figure,
    hot_cold_figure,
    main_frequency_figure,
)
from lottery_chat.config import DISPLAY_NAME, GAME_ID
from lottery_chat.loader import LoadResult, load_bytes, load_path, load_text
from lottery_chat.models import Draw

__all__ = [
    "DISPLAY_NAME",
    "GAME_ID",
    "Draw",
    "LoadResult",
    "bonus_frequencies",
    "bonus_frequency_figure",
    "filter_by_weekday",
    "heatmap_figure",
    "history_rows",
    "hot_cold",
    "hot_cold_figure",
    "load_bytes",
    "load_path",
    "load_text",
    "main_frequencies",
    "main_frequency_figure",
    "reply",
    "suggested_ticket",
    "weekday_number_matrix",
]
