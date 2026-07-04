"""Session PDF report (ReportLab) — six sections per Requirments §9.

Auto-generated at the end of Phase 5, saved to reports/. Then synced + emailed (core.sync).
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from .config import settings


def generate_report(data: dict[str, Any]) -> Path:
    """Build the PDF and return its path.

    Expected `data` keys (all optional except defaults are shown as '-'):
      session_number, lesson_name, raga, tala, overall_score, pitch_score, rhythm_score,
      thaalam_accuracy, errors (list[str]), improvements (list[str]), homework (list[str]),
      teacher_note (str), recording_drive_link (str)
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().strftime("%Y-%m-%d")
    out = settings.reports_dir / f"{today}_session_{data.get('session_number', 'x')}.pdf"

    styles = getSampleStyleSheet()
    h = ParagraphStyle("h", parent=styles["Heading2"], textColor=colors.HexColor("#8B4513"))
    body = ParagraphStyle("b", parent=styles["BodyText"], fontSize=11, leading=15)

    doc = SimpleDocTemplate(
        str(out), pagesize=A4,
        topMargin=18 * mm, bottomMargin=18 * mm, leftMargin=18 * mm, rightMargin=18 * mm,
    )
    flow: list[Any] = []

    def rule():
        flow.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#D4A017")))
        flow.append(Spacer(1, 6))

    flow.append(Paragraph("ARUVI CARNATIC MUSIC — SESSION REPORT", styles["Title"]))
    flow.append(Paragraph(
        f"Date: {today} &nbsp;|&nbsp; Session #{data.get('session_number', '-')} "
        f"&nbsp;|&nbsp; Teacher: MS Amma", body))
    flow.append(Spacer(1, 8)); rule()

    flow.append(Paragraph("1 — Today's Summary", h))
    flow.append(Paragraph(
        f"Lesson: {data.get('lesson_name', '-')} "
        f"(Raga: {data.get('raga', '-')}, Tala: {data.get('tala', '-')})", body))
    flow.append(Paragraph(f"Overall: {data.get('overall_score', '-')}", body))
    flow.append(Spacer(1, 8)); rule()

    flow.append(Paragraph("2 — Performance", h))
    flow.append(Paragraph(f"Pitch: {data.get('pitch_score', '-')}", body))
    flow.append(Paragraph(f"Rhythm: {data.get('rhythm_score', '-')}", body))
    flow.append(Paragraph(f"Thaalam: {data.get('thaalam_accuracy', '-')}", body))
    flow.append(Spacer(1, 8)); rule()

    for title, key in [("3 — Things to practice", "errors"),
                       ("4 — Improvements from last session", "improvements"),
                       ("5 — Homework for next week", "homework")]:
        flow.append(Paragraph(title, h))
        for item in (data.get(key) or ["-"]):
            flow.append(Paragraph(f"• {item}", body))
        flow.append(Spacer(1, 8)); rule()

    flow.append(Paragraph("6 — Teacher's Note to Parent", h))
    flow.append(Paragraph(data.get("teacher_note", "-"), body))

    if data.get("recording_drive_link"):
        flow.append(Spacer(1, 8)); rule()
        flow.append(Paragraph("Audio Recording", h))
        flow.append(Paragraph(str(data["recording_drive_link"]), body))

    doc.build(flow)
    return out
