"""
Streamlit UI components for the Personal AI OS.
"""
from __future__ import annotations

import streamlit as st


MODES = ["manager", "learning", "finance", "consulting"]

MODE_DESCRIPTIONS = {
    "manager": "🧠 Chief-of-Staff — priorities, balance, strategy",
    "learning": "📚 Learning — concepts, summaries, plans",
    "finance": "💰 Finance — personal, business, forecasts",
    "consulting": "💼 Consulting — offers, positioning, clients",
}

MODE_ICONS = {
    "manager": "🧠",
    "learning": "📚",
    "finance": "💰",
    "consulting": "💼",
}


def render_sidebar() -> dict:
    """
    Render the sidebar and return user configuration choices.

    Returns
    -------
    dict with keys:
      - mode: str
      - uploaded_file: UploadedFile | None
      - voice_file: UploadedFile | None
      - clear_memory: bool
    """
    st.sidebar.title("⚙️ Configuration")

    st.sidebar.markdown("### Mode")
    mode = st.sidebar.radio(
        "Select agent mode",
        options=MODES,
        format_func=lambda m: MODE_DESCRIPTIONS[m],
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📎 File Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Upload a PDF or TXT file",
        type=["pdf", "txt"],
        help="The file content will be added to your message.",
    )

    st.sidebar.markdown("### 🎙️ Voice Input")
    voice_file = st.sidebar.file_uploader(
        "Upload an audio file",
        type=["wav", "mp3", "m4a", "ogg", "webm"],
        help="Audio will be transcribed and used as your message.",
        key="voice_uploader",
    )

    st.sidebar.markdown("---")
    clear_memory = st.sidebar.button("🗑️ Clear conversation memory")

    return {
        "mode": mode,
        "uploaded_file": uploaded_file,
        "voice_file": voice_file,
        "clear_memory": clear_memory,
    }


def render_header(mode: str) -> None:
    """Render the main page title and mode description."""
    icon = MODE_ICONS.get(mode, "🤖")
    st.title(f"{icon} Personal AI OS")
    st.caption(f"**Active mode:** {MODE_DESCRIPTIONS[mode]}")
    st.divider()


def render_chat_history() -> None:
    """Render chat messages stored in session state."""
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def render_response(response: str) -> None:
    """Display assistant response and store it in session state."""
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
