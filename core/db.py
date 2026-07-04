"""SQLite persistence: schema, seeding, lookups, and session logging."""
from __future__ import annotations

import csv
import json
import sqlite3

from .config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS lessons (
    lesson_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_number        INTEGER,
    lesson_name          TEXT NOT NULL,
    raga                 TEXT,
    tala                 TEXT,
    stage                INTEGER,                       -- curriculum Stage 0-8 (SYLLABUS.md)
    track                TEXT,                          -- A|B|C|D
    source               TEXT CHECK(source IN ('book','syllabus')),
    notation             TEXT,
    lyrics               TEXT,
    reference_clip_path  TEXT,
    status               TEXT CHECK(status IN ('locked','in_progress','mastered')) DEFAULT 'locked',
    first_attempted_date TEXT,
    mastered_date        TEXT
);

CREATE TABLE IF NOT EXISTS session_log (
    session_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    date                  TEXT,
    lesson_id             INTEGER,
    duration_minutes      INTEGER,
    attempts_count        INTEGER,
    pitch_accuracy_score  REAL,
    rhythm_accuracy_score REAL,
    overall_score         REAL,
    errors_noted          TEXT,                         -- JSON array
    homework_assigned     TEXT,
    homework_reviewed     INTEGER DEFAULT 0,
    thaalam_accuracy      TEXT CHECK(thaalam_accuracy IN ('consistent','mostly_correct','needs_work')),
    recording_path_local  TEXT,
    recording_path_drive  TEXT,
    pdf_report_path_drive TEXT,
    summary               TEXT,
    FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id)
);
"""


def connect() -> sqlite3.Connection:
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(seed: bool = True) -> None:
    conn = connect()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        if seed:
            _seed_lessons(conn)
    finally:
        conn.close()


def _seed_lessons(conn: sqlite3.Connection) -> None:
    if conn.execute("SELECT COUNT(*) AS n FROM lessons").fetchone()["n"] > 0:
        return  # already seeded
    if not settings.lessons_seed.exists():
        return
    with open(settings.lessons_seed, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        conn.execute(
            """INSERT INTO lessons
               (lesson_number, lesson_name, raga, tala, stage, track, source,
                notation, lyrics, reference_clip_path, status)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                r.get("lesson_number") or None,
                r["lesson_name"],
                r.get("raga") or None,
                r.get("tala") or None,
                r.get("stage") or None,
                r.get("track") or None,
                r.get("source") or None,
                r.get("notation") or None,
                r.get("lyrics") or None,
                r.get("reference_clip_path") or None,
                r.get("status") or "locked",
            ),
        )
    conn.commit()


def current_lesson(conn: sqlite3.Connection):
    """The active Track-A repertoire lesson (the one Aruvi is working on)."""
    return conn.execute(
        "SELECT * FROM lessons WHERE status='in_progress' AND track='A' "
        "ORDER BY stage, lesson_number LIMIT 1"
    ).fetchone()


def log_session(conn: sqlite3.Connection, **fields) -> int:
    keys = ", ".join(fields)
    qmarks = ", ".join("?" for _ in fields)
    vals = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in fields.values()]
    cur = conn.execute(f"INSERT INTO session_log ({keys}) VALUES ({qmarks})", vals)
    conn.commit()
    return cur.lastrowid
