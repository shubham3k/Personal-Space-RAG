"""Streamlit documents page."""

from pathlib import Path

import requests
import streamlit as st

from ui.components.sidebar import render_sidebar

st.set_page_config(page_title="Documents", layout="wide")
settings = render_sidebar()
st.title("Documents")

if st.button("Ingest data/raw"):
    with st.spinner("Ingesting documents..."):
        response = requests.post(f"{settings['api_url']}/ingest", json={}, timeout=600)
        if response.ok:
            st.success(response.json())
        else:
            st.error(response.text)

uploaded = st.file_uploader("Add document", type=["md", "txt", "pdf", "json", "csv"])
if uploaded:
    target = Path("data/raw/uploads")
    target.mkdir(parents=True, exist_ok=True)
    file_path = target / uploaded.name
    file_path.write_bytes(uploaded.getbuffer())
    response = requests.post(f"{settings['api_url']}/ingest", json={"path": str(file_path)}, timeout=600)
    st.success(response.json() if response.ok else response.text)

docs = requests.get(f"{settings['api_url']}/documents", timeout=30)
if docs.ok:
    st.dataframe(docs.json()["documents"], use_container_width=True)
else:
    st.info("Start the API server to view indexed documents.")
