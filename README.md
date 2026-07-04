# 🎵 Aruvi AI Carnatic Music Teacher — "MS Amma"

An AI Carnatic vocal teacher for **Aruvi (age 7)**, embodying **Dr. M.S. Subbulakshmi ("MS Amma")**
as a PhD-level guru. Runs a structured 1-hour Sunday class, listens to Aruvi sing, corrects gently
in Tamil-English, tracks progress, and emails a PDF report to her parents.

- **Curriculum:** [SYLLABUS.md](SYLLABUS.md) — a graded Stage 0–8 syllabus (the *Ganamrudha Bodhini*
  book is one resource within it).
- **Build/architecture guidance:** [CLAUDE.md](CLAUDE.md) — read this first if you're developing.
- **Original requirements:** [Requirments.md](Requirments.md).

## Status
v1 scaffold. Core modules and a Streamlit UI skeleton are in place; live wiring (browser audio
capture, full session loop) is in progress. See CLAUDE.md §8 for the build plan.

## Setup
1. Install **Python 3.10+** and **ffmpeg** (ffmpeg is required by Whisper).
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your `ANTHROPIC_API_KEY`.
4. (For Drive sync + Gmail report) place a Google OAuth `credentials.json` in the project root.

## Run
```bash
streamlit run app.py
```
The app initializes the local SQLite DB (seeded from `data/lessons_seed.csv`) on first launch.

## Project layout
```
app.py              Streamlit UI (Home / Session / Progress / Lessons / Settings)
core/
  config.py         central settings (model, durations, BPM, paths) — never hardcode
  persona.py        MS Amma system prompt (single source of truth)
  pedagogy.py       Anthropic API wrapper (cached persona, per-phase prompts)
  session_manager.py 5-phase state machine + timer + break
  thaalam.py        Adi Thaalam beat pattern + animator states
  pitch.py          librosa singing analysis (guidance mode)
  transcribe.py     Whisper (spoken replies only)
  tts.py            gTTS + pre-recorded clip lookup
  report.py         ReportLab PDF generation
  sync.py           Google Drive upload + Gmail send
  audio_capture.py  browser-mic (streamlit-webrtc) helpers
data/
  lessons_seed.csv  curriculum seed (book + syllabus items)
```

## Privacy
Aruvi's recordings and photo stay local or on the parents' personal Google Drive only. Secrets live
in `.env` / `credentials.json` (gitignored). No analytics, no third-party data sharing.
