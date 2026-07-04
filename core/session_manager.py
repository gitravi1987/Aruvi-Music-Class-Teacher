"""Session state machine: 5 phases, monotonic timer, parent override, mid-session break.

Pure logic — no UI, no audio. The Streamlit layer reads this to render the session.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .config import settings


class Phase(str, Enum):
    WARMUP = "warmup"
    HOMEWORK = "homework"
    LESSON = "lesson"
    NEW = "new"
    WRAPUP = "wrapup"
    DONE = "done"


PHASE_ORDER = (Phase.WARMUP, Phase.HOMEWORK, Phase.LESSON, Phase.NEW, Phase.WRAPUP)

PHASE_LABELS = {
    Phase.WARMUP: "Phase 1: Warm-Up",
    Phase.HOMEWORK: "Phase 2: Homework Review",
    Phase.LESSON: "Phase 3: Lesson Practice",
    Phase.NEW: "Phase 4: New Content",
    Phase.WRAPUP: "Phase 5: Wrap-Up",
    Phase.DONE: "Class complete",
}


@dataclass
class SessionManager:
    started_at: float = field(default_factory=time.monotonic)
    phase_index: int = 0
    paused: bool = False
    paused_total: float = 0.0
    _paused_at: Optional[float] = None
    break_taken: bool = False

    @property
    def phase(self) -> Phase:
        if self.phase_index >= len(PHASE_ORDER):
            return Phase.DONE
        return PHASE_ORDER[self.phase_index]

    @property
    def label(self) -> str:
        return PHASE_LABELS[self.phase]

    def elapsed_seconds(self) -> float:
        now = self._paused_at if (self.paused and self._paused_at is not None) else time.monotonic()
        return now - self.started_at - self.paused_total

    def elapsed_minutes(self) -> float:
        return self.elapsed_seconds() / 60.0

    def total_minutes(self) -> int:
        return sum(settings.phase_minutes)

    def phase_should_advance(self) -> bool:
        """True when the cumulative time budget through the current phase is exceeded."""
        if self.phase is Phase.DONE:
            return False
        budget = sum(settings.phase_minutes[: self.phase_index + 1])
        return self.elapsed_minutes() >= budget

    def advance(self) -> Phase:
        """Auto-advance or parent 'Next Phase' override."""
        if self.phase_index < len(PHASE_ORDER):
            self.phase_index += 1
        return self.phase

    def back(self) -> Phase:
        """Parent 'Previous Phase' override."""
        if self.phase_index > 0:
            self.phase_index -= 1
        return self.phase

    def pause(self) -> None:
        if not self.paused:
            self.paused = True
            self._paused_at = time.monotonic()

    def resume(self) -> None:
        if self.paused and self._paused_at is not None:
            self.paused_total += time.monotonic() - self._paused_at
            self.paused = False
            self._paused_at = None

    def break_due(self) -> bool:
        """The optional ~2-min break at minute 30."""
        return (not self.break_taken) and self.elapsed_minutes() >= settings.break_at_minute

    def take_break(self) -> None:
        self.break_taken = True
