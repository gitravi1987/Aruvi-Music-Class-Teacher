"""Text-to-speech for MS Amma.

gTTS (online, Tamil) with a pre-recorded clip lookup for fixed phrases / Tamil music
terms (more authentic than synthetic speech). Returns a path the UI can play.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

from .config import settings


def _cache_path(text: str, lang: str) -> Path:
    digest = hashlib.sha1(f"{lang}:{text}".encode("utf-8")).hexdigest()[:16]
    settings.clips_dir.mkdir(parents=True, exist_ok=True)
    return settings.clips_dir / f"tts_{lang}_{digest}.mp3"


def speak(text: str, lang: str = "ta", clip: Optional[str] = None) -> Path:
    """Synthesize `text` to an mp3 and return its path.

    `clip`: optional filename of a pre-recorded clip in data/clips/ to use verbatim
    (for authentic fixed phrases). Falls back to gTTS, cached by content hash.
    """
    if clip:
        pre = settings.clips_dir / clip
        if pre.exists():
            return pre

    out = _cache_path(text, lang)
    if out.exists():
        return out

    from gtts import gTTS  # lazy import so the module loads without the dependency
    gTTS(text=text, lang=lang).save(str(out))
    return out
