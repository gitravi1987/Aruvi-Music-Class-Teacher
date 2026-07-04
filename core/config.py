"""Central configuration. Import `settings` everywhere; never hardcode values.

Loaded from environment (.env) where relevant. See .env.example.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Project root = parent of the `core/` package.
ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    # --- Claude / pedagogy ---
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    model: str = os.getenv("ARUVI_MODEL", "claude-sonnet-4-6")
    max_tokens: int = 1000  # short, child-friendly turns

    # --- Student ---
    student_name: str = "Aruvi"
    student_age: int = 7
    current_stage: int = 3  # SYLLABUS.md — Geethams

    # --- Session pacing (minutes): warmup, homework, lesson, new, wrapup ---
    phase_minutes: tuple = (10, 10, 25, 10, 5)
    break_at_minute: int = 30
    break_minutes: int = 2

    # --- Adi Thaalam BPM ---
    bpm_teaching: int = 30
    bpm_practice: int = 60
    bpm_performance: int = 90

    # --- Audio ---
    sample_rate: int = 44100

    # --- Pitch analysis (GUIDANCE MODE in v1; advisory only) ---
    pitch_tolerance_cents: int = 25
    child_fmin_hz: float = 220.0   # ~A3
    child_fmax_hz: float = 880.0   # ~A5

    # --- Mastery (parent-confirmed; not auto-gated in v1) ---
    mastery_threshold: float = 0.80
    mastery_consecutive_sessions: int = 2

    # --- Paths ---
    db_path: Path = ROOT / "data" / "aruvi.db"
    lessons_seed: Path = ROOT / "data" / "lessons_seed.csv"
    recordings_dir: Path = ROOT / "recordings"
    reports_dir: Path = ROOT / "reports"
    clips_dir: Path = ROOT / "data" / "clips"
    assets_dir: Path = ROOT / "assets"
    # Imagery. Drop a high-res illustrated portrait at assets/ms_amma.png to override.
    ms_amma_avatar: Path = ROOT / "Aruvi & MS Subbulakshmi Image" / "MS Subbulakshmi.jfif"
    aruvi_photo: Path = ROOT / "Aruvi & MS Subbulakshmi Image" / "COLOR_POP.jpg"
    credentials_path: Path = ROOT / "credentials.json"
    token_path: Path = ROOT / "token.json"

    # --- Delivery ---
    drive_folder: str = "Aruvi Music"
    parent_emails: tuple = field(default_factory=lambda: tuple(
        e.strip()
        for e in os.getenv("PARENT_EMAILS", "raveykumar@yahoo.com").split(",")
        if e.strip()
    ))


settings = Settings()
