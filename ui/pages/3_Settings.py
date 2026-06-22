"""Streamlit settings page."""

import requests
import streamlit as st

from ui.components.sidebar import render_sidebar

st.set_page_config(page_title="Settings", layout="wide")
settings = render_sidebar()
st.title("Settings")

try:
    response = requests.get(f"{settings['api_url']}/health", timeout=60)
    if response.ok:
        st.json(response.json())
    else:
        st.error(response.text)
except Exception as exc:
    st.error(f"API unavailable: {exc}")
