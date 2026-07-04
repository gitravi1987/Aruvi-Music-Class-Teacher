"""Singing analysis — GUIDANCE MODE (v1).

Returns gentle, advisory observations only. Carnatic gamakas and a child's voice make
strict cent-based scoring unreliable, so v1 reports tendencies, not hard scores. Calibrate
on Aruvi's real recordings before trusting any number (see CLAUDE.md §9 / SYLLABUS.md §8).

NOTE: this analyzes SINGING. Spoken replies go to core.transcribe (Whisper), never here.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from .config import settings

PathLike = Union[str, Path]


def analyze_singing(wav_path: PathLike, reference_wav: Optional[PathLike] = None) -> dict:
    """Extract a rough pitch/timing picture and return child-friendly guidance.

    Returns a dict consumed by core.pedagogy (MS Amma translates it for Aruvi):
      {summary, steadiness, in_tune, timing, observations: [...], scores_are_advisory: True}
    `reference_wav` is accepted for future contour comparison; unused in v1 guidance mode.
    """
    import librosa
    import numpy as np

    y, sr = librosa.load(str(wav_path), sr=settings.sample_rate, mono=True)
    if y.size == 0:
        return {
            "summary": "I couldn't hear the singing clearly, kanna. Let's try again!",
            "observations": [],
            "scores_are_advisory": True,
        }

    f0, _voiced_flag, _voiced_prob = librosa.pyin(
        y, sr=sr, fmin=settings.child_fmin_hz, fmax=settings.child_fmax_hz
    )
    voiced = f0[~np.isnan(f0)]

    observations: list[str] = []
    steadiness = "steady"
    in_tune = "mostly"

    if voiced.size:
        cents = 1200.0 * np.log2(voiced / np.nanmedian(voiced))
        spread = float(np.nanstd(cents))
        if spread > 60:
            steadiness = "wavery"
            observations.append("The held notes wobble a little — try to keep each swara still.")
        elif spread > 35:
            steadiness = "a little wavery"
    else:
        in_tune = "needs_work"
        observations.append("I couldn't catch a clear pitch — sing a little louder, kanna.")

    onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")
    timing = "even" if onsets.size >= 2 else "unclear"

    return {
        "summary": "Nice singing, kanna! Here is what MS Amma noticed.",
        "steadiness": steadiness,
        "in_tune": in_tune,
        "timing": timing,
        "observations": observations,
        "scores_are_advisory": True,
    }
