"""Source rendering helpers."""

import streamlit as st


def render_source(source: dict) -> None:
    with st.expander(f"[{source.get('number')}] {source.get('title', 'Untitled')}"):
        st.caption(source.get("source_path", ""))
        st.progress(min(1.0, max(0.0, float(source.get("score", 0)))))
