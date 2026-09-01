from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from lottery_chat.analyzer import history_rows
from lottery_chat.chat import reply
from lottery_chat.charts import (
    bonus_frequency_figure,
    heatmap_figure,
    hot_cold_figure,
    main_frequency_figure,
)
from lottery_chat.config import DISPLAY_NAME, OPERATOR
from lottery_chat.loader import LoadResult, load_bytes, load_path, merge_results
from lottery_chat.models import Draw

ROOT = Path(__file__).resolve().parent
SAMPLE_PATH = ROOT / "data" / "sample_quebec49.txt"

st.set_page_config(page_title=f"{DISPLAY_NAME} chat", layout="wide")


def _init_state() -> None:
    if "draws" not in st.session_state:
        st.session_state.draws = []
    if "load_notes" not in st.session_state:
        st.session_state.load_notes = LoadResult()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "history_focus" not in st.session_state:
        st.session_state.history_focus = False
    if "graphs_focus" not in st.session_state:
        st.session_state.graphs_focus = False
    if not st.session_state.draws and SAMPLE_PATH.exists():
        _load_sample()


def _apply_load(result: LoadResult) -> None:
    st.session_state.draws = result.draws
    st.session_state.load_notes = result


def _load_sample() -> None:
    if SAMPLE_PATH.exists():
        _apply_load(load_path(SAMPLE_PATH))


_init_state()

st.title(f"{DISPLAY_NAME} ({OPERATOR})")
st.caption(
    "Frequency stats from your files only. Draws are random — “best” does not mean more likely to win."
)

with st.sidebar:
    st.header("Data files")
    st.write("Upload Notepad `.txt` or `.csv` history. One draw per line.")
    uploads = st.file_uploader(
        "Draw history",
        type=["txt", "csv"],
        accept_multiple_files=True,
    )
    folder = st.text_input("Or folder of .txt/.csv files", value=str(ROOT / "data"))
    col_a, col_b = st.columns(2)
    with col_a:
        load_clicked = st.button("Load files", type="primary")
    with col_b:
        sample_clicked = st.button("Load sample")

    if sample_clicked:
        _load_sample()
        st.session_state.messages = []
    elif load_clicked:
        results: list[LoadResult] = []
        for upload in uploads or []:
            results.append(load_bytes(upload.getvalue(), source=upload.name))
        folder_path = Path(folder.strip()) if folder.strip() else None
        if folder_path and folder_path.is_dir():
            for path in sorted(folder_path.glob("*")):
                if path.suffix.lower() in {".txt", ".csv"}:
                    results.append(load_path(path))
        if results:
            _apply_load(merge_results(*results))
            st.session_state.messages = []
        else:
            st.warning("No files found to load.")

    draws: list[Draw] = st.session_state.draws
    notes: LoadResult = st.session_state.load_notes
    st.metric("Draws loaded", len(draws))
    if notes.warnings:
        st.caption(f"{len(notes.warnings)} weekday warning(s)")
    if notes.errors:
        with st.expander(f"Skipped lines ({notes.skipped})"):
            for err in notes.errors[:40]:
                st.text(err)

draws = st.session_state.draws
tab_chat, tab_history, tab_graphs = st.tabs(["Chat", "History", "Graphs"])

with tab_chat:
    st.write(
        "Ask in English or French: best numbers, Wednesday / mercredi, Saturday / samedi, "
        "history, or graphs."
    )
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    prompt = st.chat_input("What are the best Québec 49 numbers for Saturday?")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        answer = reply(prompt, draws)
        st.session_state.messages.append({"role": "assistant", "content": answer.text})
        st.session_state.history_focus = answer.show_history
        st.session_state.graphs_focus = answer.show_graphs
        st.rerun()

with tab_history:
    if not draws:
        st.info("Load a history file to see all draws.")
    else:
        df = pd.DataFrame(history_rows(draws))
        st.dataframe(df, use_container_width=True, hide_index=True)
        if st.session_state.history_focus:
            st.caption("Opened from chat — this is the full loaded history.")

with tab_graphs:
    if not draws:
        st.info("Load a history file to plot frequencies.")
    else:
        st.plotly_chart(main_frequency_figure(draws), use_container_width=True)
        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(main_frequency_figure(draws, "wednesday"), use_container_width=True)
        with g2:
            st.plotly_chart(main_frequency_figure(draws, "saturday"), use_container_width=True)
        st.plotly_chart(bonus_frequency_figure(draws), use_container_width=True)
        st.plotly_chart(hot_cold_figure(draws), use_container_width=True)
        st.plotly_chart(heatmap_figure(draws), use_container_width=True)
        if st.session_state.graphs_focus:
            st.caption("Opened from chat — frequencies use only the loaded Québec 49 file(s).")
