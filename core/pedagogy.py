"""MS Amma pedagogy engine — wraps the Anthropic API.

Sends the stable persona as a *cached* system prompt; per-turn context (phase, lesson,
audio analysis, recent history) goes in the messages array. Uses the official `anthropic`
SDK (never raw HTTP). Model defaults to claude-sonnet-4-6 (see core/config.py).
"""
from __future__ import annotations

import json
from typing import Any, Optional

import anthropic

from .config import settings
from .persona import PERSONA_SYSTEM_PROMPT

PHASE_GUIDES = {
    "warmup": "PHASE 1 — Warm-Up. Greet Aruvi. Lead Sa-Ri-Ga-Ma varisai and one cycle of Adi "
              "Thaalam at 30 BPM. Give brief, happy feedback. No scoring this phase.",
    "homework": "PHASE 2 — Homework Review. Ask Aruvi to sing last week's homework piece. After "
                "she sings, give the top 2-3 gentle corrections only.",
    "lesson": "PHASE 3 — Lesson Practice. Continue the current lesson. Demonstrate, then let her "
              "attempt. Break down corrections: pitch first, then rhythm, then phrasing. Repeat the "
              "hard part (max 3 tries) and encourage.",
    "new": "PHASE 4 — New Content. If today's lesson is going well, introduce the next lesson's "
           "first 2-4 lines, line by line, repeat-after-me. Otherwise revisit the hardest part.",
    "wrapup": "PHASE 5 — Wrap-Up. Summarise today in 3-4 child-friendly sentences. Assign specific "
              "homework (which piece, how many times a day, what to focus on). Say goodbye.",
}


class MSAmma:
    """Stateless-per-call teacher. Pass conversation `history` in each turn."""

    def __init__(self, model: Optional[str] = None):
        # Reads ANTHROPIC_API_KEY from the environment.
        self.client = anthropic.Anthropic()
        self.model = model or settings.model

    def _system(self) -> list[dict]:
        # Cached system prompt — keep its bytes stable across the whole session.
        return [{
            "type": "text",
            "text": PERSONA_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }]

    def respond(
        self,
        phase: str,
        history: Optional[list[dict]] = None,
        student_said: Optional[str] = None,
        analysis: Optional[dict] = None,
        session_summary: Optional[str] = None,
        lesson_name: Optional[str] = None,
        use_thinking: bool = False,
    ) -> str:
        """Produce MS Amma's next spoken turn (Tamil-English).

        history: prior [{"role", "content"}] turns (we keep ~the last 10).
        student_said: transcript of Aruvi's *spoken* reply (not her singing).
        analysis: guidance dict from core.pitch (MS Amma translates, never reads numbers aloud).
        """
        history = history or []
        ctx = [PHASE_GUIDES.get(phase, "")]
        ctx.append(
            f"Student: {settings.student_name}, age {settings.student_age}, "
            f"curriculum Stage {settings.current_stage}."
        )
        if lesson_name:
            ctx.append(f"Current lesson: {lesson_name}.")
        if session_summary:
            ctx.append(f"Last session summary: {session_summary}")
        if analysis:
            ctx.append(
                "Audio analysis notes (translate into kind, child-friendly words; "
                "do NOT read numbers aloud):\n" + json.dumps(analysis, ensure_ascii=False)
            )
        if student_said:
            ctx.append(f'Aruvi said: "{student_said}"')
        ctx.append("Respond as MS Amma for this moment of the class.")

        messages = list(history[-10:])
        messages.append({"role": "user", "content": "\n\n".join(p for p in ctx if p)})

        kwargs: dict[str, Any] = dict(
            model=self.model,
            max_tokens=settings.max_tokens,
            system=self._system(),
            messages=messages,
        )
        if use_thinking:
            # Adaptive thinking (supported on Sonnet 4.6 / Opus 4.8 / Fable 5).
            kwargs["thinking"] = {"type": "adaptive"}

        resp = self.client.messages.create(**kwargs)
        return "".join(b.text for b in resp.content if b.type == "text").strip()

    def summarize_session(self, history: list[dict]) -> str:
        """Persist a short summary for next session's context (kept out of live history)."""
        messages = list(history[-20:])
        messages.append({
            "role": "user",
            "content": "In 3-4 short sentences, summarise today's class for next week's context: "
                       "what was practiced, what improved, and what to focus on next. Plain English.",
        })
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            system=self._system(),
            messages=messages,
        )
        return "".join(b.text for b in resp.content if b.type == "text").strip()
