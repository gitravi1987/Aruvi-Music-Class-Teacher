"""Adi Thaalam — 8 beats, Chaturasra Laghu (4) + 2 Drutams (2+2) — hand-kept pattern.

v1 thaalam scope. Drives the ThaalaAnimator in the UI and MS Amma's spoken cues.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ThaalaState(str, Enum):
    IDLE = "idle"            # hand shown, no highlight, awaiting start
    TEACHING = "teaching"    # 30 BPM, each beat highlighted with a pause
    PRACTICE = "practice"    # 60 BPM, continuous loop
    TEST = "test"            # animation hidden; Aruvi keeps tala; parent confirms


@dataclass(frozen=True)
class Beat:
    number: int      # 1..8 within the avartanam
    gesture: str     # what the hand does
    cue: str         # short spoken cue


# Adi Thaalam = 4 + 2 + 2
ADI_BEATS = (
    Beat(1, "clap (palm on thigh)",        "Thattu"),
    Beat(2, "little finger tap",           "Tap 1"),
    Beat(3, "ring finger tap",             "Tap 2"),
    Beat(4, "middle finger tap",           "Tap 3"),
    Beat(5, "clap (wave, back of hand)",   "Veechu"),
    Beat(6, "clap (palm)",                 "Thattu"),
    Beat(7, "clap (wave, back of hand)",   "Veechu"),
    Beat(8, "clap (palm)",                 "Thattu"),
)

BEATS_PER_CYCLE = len(ADI_BEATS)  # 8


def beat(n: int) -> Beat:
    """1-indexed beat within the 8-beat avartanam (wraps)."""
    return ADI_BEATS[(n - 1) % BEATS_PER_CYCLE]


def seconds_per_beat(bpm: int) -> float:
    return 60.0 / bpm


# MS Amma's teaching script (Tamil-English) — see Requirments §7.5
TEACHING_SCRIPT = (
    "கண்ணா, இப்போ thaalam போடுவோம். Right hand-ஐ பாரு. "
    "Beat 1: Thattu — thigh-ல தட்டு. "
    "Beat 2, 3, 4: little finger, ring finger, middle finger — slowly tap. "
    "Beat 5: Veechu — hand-ஐ திரும்பு. Beat 6: Thattu. Beat 7: Veechu. "
    "Beat 8: Thattu — and we start again! Ready? Follow MS Amma's hand. Sa... Ri... Ga..."
)
