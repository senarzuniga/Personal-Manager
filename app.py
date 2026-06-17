"""
Personal AI Operating System — main entry point.

Run with:
    streamlit run app.py
"""
from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from core.orchestrator import build_orchestrator
from tools.file_handler import extract_text
from tools.voice_handler import transcribe_audio
from ui.app_ui import (
    render_sidebar,
    render_header,
    render_chat_history,
    render_response,
)

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="Personal AI OS",
    page_icon="🧠",
    layout="wide",
)


def _init_state() -> None:
    """Initialise Streamlit session state on first run."""
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = build_orchestrator()
    if "messages" not in st.session_state:
        st.session_state.messages = []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    _init_state()

    orchestrator = st.session_state.orchestrator

    # ── Sidebar ──────────────────────────────────────────────────────────
    config = render_sidebar()
    mode: str = config["mode"]
    uploaded_file = config["uploaded_file"]
    voice_file = config["voice_file"]
    clear_memory: bool = config["clear_memory"]

    if clear_memory:
        orchestrator.memory.clear()
        st.session_state.messages = []
        st.success("Conversation memory cleared.")

    # ── Header ───────────────────────────────────────────────────────────
    render_header(mode)

    # ── Chat history ─────────────────────────────────────────────────────
    render_chat_history()

    # ── Input resolution ─────────────────────────────────────────────────
    # Priority: voice > text input. File content is appended to whichever.

    user_text: str | None = None

    # 1. Voice transcription
    if voice_file is not None:
        audio_bytes = voice_file.read()
        with st.spinner("🎙️ Transcribing audio…"):
            try:
                user_text = transcribe_audio(audio_bytes, voice_file.name)
                st.info(f"📝 Transcribed: *{user_text}*")
            except Exception as exc:
                st.error(f"Voice transcription failed: {exc}")

    # 2. File content extraction (append to message)
    file_context: str = ""
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        with st.spinner("📄 Extracting file content…"):
            try:
                file_context = extract_text(file_bytes, uploaded_file.name)
                st.success(f"✅ File loaded: {uploaded_file.name} ({len(file_context):,} chars)")
            except Exception as exc:
                st.error(f"File extraction failed: {exc}")

    # 3. Chat input (used if no voice)
    chat_input = st.chat_input("Type your message here…")
    if chat_input:
        user_text = chat_input

    # ── Execute ──────────────────────────────────────────────────────────
    if user_text:
        # Combine user message with any extracted file context
        full_input = user_text
        if file_context:
            full_input = (
                f"{user_text}\n\n"
                f"--- Attached Document ---\n{file_context}"
            )

        # Display user message
        with st.chat_message("user"):
            st.markdown(user_text)
            if file_context:
                st.caption(f"📎 Document attached ({len(file_context):,} chars)")
        st.session_state.messages.append({"role": "user", "content": user_text})

        # Check for API key
        if not os.getenv("OPENAI_API_KEY"):
            st.error(
                "⚠️ No OpenAI API key found. "
                "Please set OPENAI_API_KEY in your .env file or environment."
            )
            return

        # Run through orchestrator
        with st.spinner("🤖 Your executive team is thinking…"):
            try:
                response = orchestrator.execute(full_input, mode)
            except Exception as exc:
                response = f"❌ An error occurred: {exc}"

        render_response(response)

    # ── Footer ───────────────────────────────────────────────────────────
    st.divider()
    st.caption(
        "Personal AI OS · Manager → Orchestrator → Specialists · "
        "Powered by OpenAI GPT-4o-mini"
    )


if __name__ == "__main__":
    main()
