"""
Voice handler — transcribes audio files using the OpenAI Whisper API.
"""
from __future__ import annotations

import os
import io
from openai import OpenAI


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """
    Transcribe audio using OpenAI's Whisper (whisper-1) model.

    Parameters
    ----------
    audio_bytes : bytes
        Raw audio content (wav, mp3, m4a, etc.).
    filename : str
        Original filename (used to set the correct MIME type).

    Returns
    -------
    str
        Transcribed text.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename  # OpenAI SDK reads the name attribute for MIME

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text",
    )
    return transcript.strip() if isinstance(transcript, str) else str(transcript)
