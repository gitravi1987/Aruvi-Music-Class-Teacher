"""Browser-side audio capture helpers (streamlit-webrtc).

We capture from the BROWSER mic so it works on the laptop AND on Aruvi's/Janani's Android
phone — NOT server-side `sounddevice`, which only sees the laptop's mic. The Streamlit UI
wires up the webrtc component; this module names recordings and persists audio to WAV.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Union

from .config import settings

PathLike = Union[str, Path]


def recording_path(phase: str, attempt: int, session_id: Union[int, str] = "x") -> Path:
    settings.recordings_dir.mkdir(parents=True, exist_ok=True)
    name = (
        f"{date.today():%Y-%m-%d}_session_{session_id}"
        f"_phase_{phase}_attempt_{attempt}.wav"
    )
    return settings.recordings_dir / name


def save_wav(samples, sr: int, out: PathLike) -> Path:
    """Persist captured audio samples (numpy array) to a WAV file."""
    import soundfile as sf  # lazy import
    sf.write(str(out), samples, sr)
    return Path(out)
