"""Streamlit chat UI."""

from pathlib import Path
import sys

# Ensure project root is on sys.path so `import ui.*` works when Streamlit runs this file.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import requests
import streamlit as st

from ui.components.sidebar import render_sidebar
from ui.components.source_card import render_source

st.set_page_config(page_title="Personal Life OS", page_icon=":brain:", layout="wide")
settings = render_sidebar()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

st.title("Personal Life OS")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask your knowledge base"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Searching your local knowledge..."):
            response = requests.post(
                f"{settings['api_url']}/query",
                json={"query": prompt, "conversation_id": st.session_state.conversation_id, "top_k": settings["top_k"]},
                timeout=180,
            )
            if response.ok:
                data = response.json()
                st.session_state.conversation_id = data["conversation_id"]
                st.markdown(data["answer"])
                st.caption(f"{data['provider']} / {data['model']}")
                for source in data.get("sources", []):
                    render_source(source)
                st.session_state.messages.append({"role": "assistant", "content": data["answer"]})
            else:
                st.error(response.text)
