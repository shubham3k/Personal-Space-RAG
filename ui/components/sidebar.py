"""Sidebar controls."""

import streamlit as st


def render_sidebar() -> dict:
    with st.sidebar:
        st.title("Personal Life OS")
        api_url = st.text_input("API URL", value="http://localhost:8000")
        top_k = st.slider("Sources", min_value=1, max_value=20, value=8)
    return {"api_url": api_url.rstrip("/"), "top_k": top_k}
