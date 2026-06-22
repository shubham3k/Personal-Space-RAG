"""Chat rendering helpers."""

import streamlit as st


def render_message(role: str, content: str) -> None:
    with st.chat_message(role):
        st.markdown(content)
