"""Whisper transcription for Aruvi's SPOKEN replies (never her singing).

Tamil ASR is error-prone, so the UI must always offer a button / parent-relay fallback.
The model is loaded lazily and cached for the process.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

PathLike = Union[str, Path]

_model = None  # cached Whisper model


def _get_model(name: str = "small"):
    global _model
    if _model is None:
        import whisper  # lazy import
        _model = whisper.load_model(name)
    return _model


def transcribe(wav_path: PathLike, language: Optional[str] = None) -> str:
    """Transcribe spoken Tamil-English. Returns text (may be empty/imperfect)."""
    model = _get_model()
    result = model.transcribe(str(wav_path), language=language)
    return (result.get("text") or "").strip()
