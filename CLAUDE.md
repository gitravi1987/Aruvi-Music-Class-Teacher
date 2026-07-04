# CLAUDE.md — Aruvi AI Carnatic Music Teacher ("MS Amma")

Guidance for any Claude Code session working on this project. Read this first, every session.

---

## 1. What this is

An AI-powered Carnatic music teacher that runs a structured **1-hour Sunday class** for
**Aruvi Kamatchi JR (age 7)**, embodying the persona of **Dr. M.S. Subbulakshmi ("MS Amma")** —
acting as a **PhD-level master guru**, not a book-reciter. It teaches from a master-designed graded
curriculum ([SYLLABUS.md](SYLLABUS.md)) that **incorporates and extends** *Ganamrudha Bodhini*
(Panchapakesa Iyer is one resource, not the boundary), listens to Aruvi sing via mic, gives gentle
corrections in Tamil-English, tracks progress, and produces a PDF report for the parents after each
session.

- **Student:** Aruvi, 7. Current level: Janta Varisai completed; Geetham Lesson 7 in progress.
- **Parents / users:** Ravikumar (builder/admin, `raveykumar@yahoo.com`) and Janani (supervisor).
- **Full requirements:** see [Requirments.md](Requirments.md). **This file overrides it** wherever
  they disagree (the requirements doc predates the decisions in §3 below).

**Status (resume point — last worked 2026-06-17):**
- **All prerequisites DONE** — see §10 (Python 3.10.11, API key+billing verified live, ffmpeg 8.1.1,
  all deps incl. PyTorch, Google Cloud creds, 55-page book PDF uploaded).
- **v1 UI built, running, styled, and INTERACTIVE** — music theme (light/high-contrast via
  `.streamlit/config.toml`), app name "Aruvi's Music Class", MS Amma avatar, 5-screen nav, phase
  **stepper**, **live timer**, working **Previous/Pause/Resume/Next/Restart** controls.
  Run: `streamlit run app.py` → http://localhost:8501 (launch with the WinGet Links dir on PATH so
  Whisper finds ffmpeg).
- **Live MS Amma conversation DONE** — Session screen has an in-browser recorder (`st.audio_input`),
  "I sang"→`core.pitch` guidance and "I spoke"→`core.transcribe` (Whisper), plus a text box; she
  replies via `core.pedagogy.MSAmma` (warm Paati-teacher persona), **auto-greets at class start**, and
  speaks via audio. Conversation state in `st.session_state.chat`.
- **Voice so far:** human-recorded **greeting.mp3 / closing.mp3** in `data/clips/` (Ravi recorded them;
  uploaded as AAC, transcoded to MP3 via ffmpeg). Dynamic replies still use robotic **gTTS**.
- **NEXT (start here tomorrow), in order:**
  1. **"Everything in human voice"** — Ravi wants ALL speech human-sounding. Dynamic replies can't be
     pre-recorded, so wire a **neural TTS** into `core/tts.py`. **Decision pending — pick a provider:**
     Google Cloud TTS (recommended — reuses existing GCP, native Tamil WaveNet, generous free tier) /
     ElevenLabs / Azure. Keep the human greeting/closing clips; neural for dynamic. (Declined: cloning
     MS Subbulakshmi's speaking voice — see §3 Voice row.)
  2. **Digitize the book** — extract notation/lyrics from `ganamarudha_bodhini.pdf` into `lessons`;
     priority = *Sri Gananatha* (Stage 3). Render pages with PyMuPDF (`fitz`), not pdftoppm.
  3. **Pitch calibration** on Aruvi's real recordings before trusting any scores.
  4. **Delivery** — wrap-up triggers `core.report` PDF → `core.sync` (Drive + Gmail; first call opens a
     one-time browser OAuth consent → `token.json`).
- Imagery: `MS Subbulakshmi.jfif` is low-res (drop a high-res illustrated portrait at
  `assets/ms_amma.png` to upgrade — the app auto-prefers it). Aruvi's photo `COLOR_POP.jpg` is local-only.

---

## 2. Golden rules (do not violate)

1. **MS Amma never breaks character.** No "As an AI…", ever. Warm, patient, maternal — like a
   loving grandmother *and* a master guru. Corrects gently, never says "wrong," never rushes,
   never shows frustration.
0. **Teach from [SYLLABUS.md](SYLLABUS.md), not just the book.** MS Amma follows the graded
   curriculum (Stages 0–8, four tracks) with PhD-level judgment; *Ganamrudha Bodhini* is one input.
   Progression is **by curriculum Stage, not by book page.**
2. **Quality over clock.** Never skip lesson content or rush a phase just to finish on time.
3. **Never advance a lesson without explicit parent unlock** (see §6 progression rules).
4. **Child-data protection.** Aruvi's voice recordings and photo stay local or on Ravi's personal
   Drive only. Never send child data to any third party beyond the Anthropic API (text) and the
   parent's own Google Drive/Gmail. No analytics, no tracking libraries.
5. **Secrets never in code or git.** API keys in `.env`; Google creds in `credentials.json`. Both in
   `.gitignore`. Confirm `.gitignore` exists before the first commit.
6. **This is for a 7-year-old.** Min 20px body text, no harsh red error marks (use amber/⚠️),
   positive reinforcement, infinite patience in the prompt.

---

## 3. Locked decisions (from the requirements interview — authoritative)

| Area | Decision |
|---|---|
| **Pedagogy model** | Default **`claude-sonnet-4-6`**; user-configurable in Settings to `claude-opus-4-8` or `claude-fable-5`. Make the model ID a single config value, never hardcoded at call sites. |
| **Platform** | Windows laptop **and Android phone browser**. → **Audio is captured in the browser** (`streamlit-webrtc` or an HTML recorder). Do **NOT** use server-side `sounddevice` as the capture path — it only sees the laptop mic and breaks the phone use case. |
| **Voice out (TTS)** | **Human-recorded clips for fixed phrases** (the warmth choice): drop `greeting.*`/`closing.*` (and later key terms) into `data/clips/`; the app plays them and falls back to **gTTS** for dynamic speech. **Do NOT synthesize or clone Dr. M.S. Subbulakshmi's speaking voice** — declined on ethical/consent/cultural grounds. Her *real archival recordings* may be used only as authentic **singing demos** (reference audio) if Ravi provides rights-clean clips. A warm neural voice (ElevenLabs/Azure/Google) remains an option for dynamic speech if Ravi wants to upgrade later. |
| **Voice in (STT)** | **Whisper** (local) transcribes Aruvi's spoken Tamil-English replies. Always provide a **button / parent-relay fallback** because Tamil transcription is error-prone. |
| **Singing vs speech** | Singing → pitch/rhythm analysis (librosa). Speech → Whisper. Never send singing to Whisper. |
| **Pitch/rhythm scoring** | **Gentle guidance first.** v1 flags obvious off-notes/timing on plain held notes and phrases corrections kindly. **Do NOT gate the 80% mastery rule on automated scores until calibrated on Aruvi's real recordings.** Gamakas + child voice make rigid cent-comparison unreliable. |
| **Reference audio** | **Both**: Ravi pre-records a reference clip per lesson where possible; TTS-spoken swara notation as fallback. Pitch analysis compares against the reference. |
| **Curriculum** | MS Amma teaches a **proprietary graded syllabus** ([SYLLABUS.md](SYLLABUS.md)) — Stages 0–8 across four tracks (Repertoire, Laya, Aural/Manodharma, Theory). She is a **PhD-level guru**, free to teach beyond the book. The book is one `source`; MS Amma authors the rest. Progress is tracked **by Stage**, not book page. Aruvi is in **Stage 3** (Geethams). |
| **Lesson content source** | Ravi will **photograph all 50+ pages of *Ganamrudha Bodhini* and upload a PDF** → digitize into the lessons DB as `source = book`. Content beyond the book (later varnams, krithis, manodharma, theory, ear-training) is authored by MS Amma as `source = syllabus`. The book PDF is a prerequisite for the book-derived lessons, **not** for the whole curriculum. |
| **Reports** | Generate PDF (ReportLab) → save local **+** sync to Google Drive **+** **auto-email to the parents via Gmail** at session end. (WhatsApp remains out of scope; email is in.) |
| **Avatar** | Source a **new high-res illustrated portrait** of MS Amma (saree-clad, with veena). The supplied `.jfif` is too low-res; the existing photo is a reference only. |
| **Pacing** | **Auto-timed phases with a parent "Next Phase" / pause override**, plus an optional **2-min break at ~minute 30** (reconcile this with the Section 6 phase plan). |
| **Build approach** | **MVP-first, then the full six weekend sprints, with state-of-the-art UX.** Not "fastest/throwaway" — build it properly and completely. Weekend 1 = a thin end-to-end MVP slice; later weekends deepen it. |

---

## 4. Tech stack (with corrected model IDs)

> The requirements doc lists outdated model IDs (`claude-opus-4-6`, `claude-fable`). **Use the IDs
> below.** Verified against the current Claude model catalog.

| Concern | Tool | Notes |
|---|---|---|
| Pedagogy engine | **Anthropic API**, `claude-sonnet-4-6` (default) | Configurable to `claude-opus-4-8` / `claude-fable-5`. Use the official `anthropic` Python SDK — never raw HTTP, never an OpenAI shim. |
| Speech-to-text | `openai-whisper` (local, base/small) | Tamil-English spoken replies only. |
| Pitch / rhythm | `librosa` | F0 + onset detection. Calibrate for child vocal range (~C4–G5). |
| Text-to-speech | `gTTS` (online) + pre-recorded clips | `pyttsx3` offline fallback is largely moot — if offline, the Claude engine is down too. |
| Browser audio | `streamlit-webrtc` (or HTML recorder) | **Capture path** — replaces `sounddevice` for the phone-browser requirement. |
| Web UI | `streamlit` | See §9 gotcha about Streamlit's rerun model vs the live timer/animation. |
| DB | `sqlite3` (stdlib) | Local. |
| PDF | `reportlab` | Auto-generated at session end. |
| Cloud + email | `google-api-python-client`, `google-auth-oauthlib` | Drive sync + Gmail send, OAuth 2.0, `credentials.json` local only. |
| Config | `python-dotenv` | `.env` for the API key. |

**Anthropic SDK conventions (important):**
- Default `max_tokens` ~1000 per pedagogy call (short, child-friendly turns).
- Use `thinking={"type": "adaptive"}` for anything that needs reasoning; Sonnet 4.6 supports it.
  Do **not** use `budget_tokens` (deprecated on 4.6).
- **Prompt-cache the system prompt + MS Amma persona block** (it's identical every call) to cut
  cost/latency. Keep the persona/system prefix byte-stable; put per-turn state (phase, analysis
  JSON, last-10-turns) after the cache breakpoint.
- Send only **last ~10 turns + a persisted session summary**, not full history.
- Parse tool/JSON outputs with `json.loads()` — never raw string-match.

---

## 5. Architecture & proposed repo layout

```
aruvi-music-teacher/
├── app.py                     # Streamlit entrypoint (screens, routing)
├── .env                       # ANTHROPIC_API_KEY (gitignored)
├── credentials.json           # Google OAuth (gitignored)
├── requirements.txt
├── CLAUDE.md / Requirments.md
├── core/
│   ├── persona.py             # MS Amma system prompt + persona block (single source of truth)
│   ├── pedagogy.py            # Anthropic API calls, conversation state, per-phase prompts
│   ├── session_manager.py     # 5-phase state machine, timer, parent override, break
│   ├── audio_capture.py       # streamlit-webrtc browser capture → WAV
│   ├── transcribe.py          # Whisper (speech only)
│   ├── pitch.py               # librosa F0/onset analysis → error JSON (guidance mode)
│   ├── tts.py                 # gTTS + pre-recorded clip lookup
│   ├── thaalam.py             # Adi Thaalam animator state (IDLE/TEACHING/PRACTICE/TEST)
│   ├── report.py              # ReportLab PDF generation
│   └── sync.py                # Google Drive upload + Gmail send
├── data/
│   ├── aruvi.db               # SQLite (gitignored)
│   ├── lessons.csv            # imported notation/lyrics (from the book PDF)
│   └── clips/                 # pre-recorded Tamil term + reference audio clips
├── reports/                   # generated PDFs (local)
├── recordings/                # local WAV recordings (gitignored)
└── assets/                    # avatar, kolam textures, fonts, icons, metronome.wav
```

Pipeline: **browser mic → WAV → (speech) Whisper / (singing) librosa → pedagogy.py (Claude) →
response → gTTS → browser audio**, orchestrated by `session_manager.py` across the 5 phases.

---

## 6. Data model (SQLite)

Use the schema in [Requirments.md §5.3](Requirments.md#L161) **plus this required addition** (the
original omits the actual lesson content, which the AI needs to teach):

```
lessons:  lesson_id, lesson_number, lesson_name, raga, tala,
          stage INTEGER,        -- curriculum Stage 0-8 (SYLLABUS.md)        ← ADDED
          track TEXT,           -- A|B|C|D repertoire/laya/aural/theory      ← ADDED
          source TEXT,          -- 'book' | 'syllabus'                       ← ADDED
          notation TEXT,        -- swara notation lines                      ← ADDED
          lyrics TEXT,          -- sahitya / lyrics                          ← ADDED
          reference_clip_path,  -- pre-recorded demo audio, nullable         ← ADDED
          status[locked|in_progress|mastered], first_attempted_date, mastered_date

session_log: session_id, date, lesson_id, duration_minutes, attempts_count,
          pitch_accuracy_score, rhythm_accuracy_score, overall_score,
          errors_noted(JSON), homework_assigned, homework_reviewed,
          thaalam_accuracy[consistent|mostly_correct|needs_work],  -- parent-rated
          recording_path_local, recording_path_drive, pdf_report_path_drive
```

**Scoring formula is currently UNDEFINED** in the spec — define it explicitly before wiring the
mastery gate, and remember the gate stays parent-confirmed during v1 (guidance-first).

**Progression rules:** lesson is `in_progress` until ≥80% across 2 consecutive sessions, then
`mastered` — but the AI **only advances after explicit parent confirmation**. Never auto-skip.

---

## 7. Session flow (5 phases, ~60 min)

1. **Warm-Up (0–10):** greeting + Sa-Ri-Ga-Ma varisai + 1 cycle Adi Thaalam @30 BPM. No scoring.
2. **Homework Review (0–20):** sing last week's piece; record; analyze; top 2–3 gentle corrections; log.
3. **Lesson Practice (20–45):** demo (reference clip or spoken swara) → Aruvi attempts → break down
   pitch→rhythm→phrasing → repeat hard segment (max 3 retries) → log each attempt. Thaalam alongside.
4. **New Content (45–55):** if ≥80% this session, introduce next lesson's first 2–4 lines; else
   revisit the hardest segment. Teach line-by-line, repeat-after-me.
5. **Wrap-Up (55–60):** 3–4 sentence summary, assign specific homework, goodbye → **auto-trigger PDF
   report → save local + Drive + email.**

Auto-timed, but Janani can pause / advance via override. Insert the **2-min break ~minute 30**.

**Fixed lines (use verbatim):**
- Greeting: `வணக்கம் கண்ணா! MS Amma இங்க இருக்கேன். இன்னைக்கு நம்ம class ஆரம்பிக்கலாமா?`
- Closing: `நீ சிறப்பாக பாடுவாய் கண்ணா! அடுத்த Sunday பார்க்கலாம். நன்றி.`

The MS Amma persona/system-prompt block lives in `core/persona.py` as the single source of truth —
see [Requirments.md §3.3](Requirments.md#L62). Append a "do not break character / 3-strikes-change-
approach" reminder.

---

## 8. Build plan — MVP first, then 6 weekend sprints, SOTA UX

**Weekend 0 (prereqs, see §10):** API key, Google creds, Python+ffmpeg, lesson-book PDF.

**MVP slice (thin end-to-end, do this first):** terminal/minimal-UI MS Amma greeting via Sonnet 4.6
→ record one song in the browser → run guidance-mode pitch check → speak feedback via gTTS →
write a basic PDF → save locally. Proves the whole pipeline before deepening any part.

Then the six sprints (from [Requirments.md §13](Requirments.md#L551)), each raising UX quality:
1. Claude API + MS Amma persona (terminal).
2. Browser mic capture + Whisper transcription.
3. librosa pitch/rhythm in **guidance mode**.
4. Full 5-phase session flow + Adi Thaalam animator.
5. PDF report + Drive sync + Gmail email.
6. Polished music-themed Streamlit UI (avatar, kolam texture, animations) — usable by Janani solo.

**UX bar:** music-classroom feel, not generic software. Palette/typography/animation specs in
[Requirments.md §11.3](Requirments.md#L479). Test Tamil fonts (Noto Sans Tamil via Google Fonts CDN)
and the thaalam SVG animation on **Android Chrome early** (Weekend 4), with a text beat-counter fallback.

---

## 9. Gotchas / known risks (from review — keep front of mind)

- **Browser ≠ server mic.** Already decided: use `streamlit-webrtc`. Never reach for `sounddevice`.
- **Streamlit reruns the whole script** on every interaction — fights the live 60-min timer,
  frame-by-frame thaalam animation, metronome, and continuous recording. Use `st.session_state`
  carefully and custom components; if it becomes painful, raise reconsidering the UI layer.
- **Pitch analysis is hard:** gamakas are intentional pitch movement (not errors), and child-voice
  F0 is noisy. Stay in guidance mode; calibrate on Aruvi's recordings before trusting numbers.
- **Latency:** Whisper + Claude + gTTS round-trip is multi-second. Pre-generate fixed phase
  transitions, show a "thinking…" indicator, never block the UI on the API.
- **gTTS voice** is generic — set expectations; lean on pre-recorded clips for key phrases.
- **Drive/Gmail:** sync/email only **after** the session ends (never mid-session). Handle OAuth token
  expiry with a "Re-authenticate" button; on failure, save locally and flag "Sync/Email pending."
- **Windows console can't print Tamil** (cp1252) — ad-hoc `python` scripts that `print()` Tamil
  fail with `UnicodeEncodeError`. Set `PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8` for CLI tests. The
  Streamlit app renders in the browser, so it's unaffected.
- **Numbering in `Requirments.md`** is inconsistent (duplicate §4 and §8) — harmless, ignore.

---

## 10. Prerequisites & setup status

| Prereq | Status | Action |
|---|---|---|
| Microphone | ✅ Done | Set up on the laptop. |
| Anthropic API key | ✅ Done | Key in `.env`; verified with a live `claude-sonnet-4-6` call. Billing active. |
| Google Cloud + Drive/Gmail creds | ✅ Done | GCP project + Gmail/Drive APIs enabled; OAuth consent (External/Testing, self as test user); Desktop OAuth client downloaded as `credentials.json` (verified `installed` type). Host account is a Gmail; reports email to the Yahoo address as recipient. First Drive/Gmail call triggers a one-time browser OAuth consent → writes `token.json`. |
| Python 3.10+ | ✅ Done | Python **3.10.11** confirmed installed. |
| ffmpeg | ✅ Done | ffmpeg **8.1.1** installed via `winget Gyan.FFmpeg`, on the user PATH (open a fresh terminal so PATH refreshes; Whisper finds it then). |
| Python deps | ✅ Done | Full `pip install -r requirements.txt` complete and verified importable (incl. `torch 2.12.0+cpu`, librosa, whisper, streamlit, streamlit-webrtc, gTTS, google-api). |
| Lesson-book PDF | ✅ Uploaded; digitization pending | `ganamarudha_bodhini.pdf` (55 pages, ~16 MB) in root; scan is legible (incl. Tamil + the 72-Melakarta table). Render pages with PyMuPDF (`fitz`) → `data/book_pages/*.png` (pdftoppm/poppler is NOT installed; use PyMuPDF). **Next:** digitize notation/lyrics into the `lessons` table, priority first = Aruvi's current Geethams (Stage 3). |
| Illustrated MS Amma avatar | ⏳ Pending | Source/generate a high-res illustrated portrait. |

**When guiding Ravi through setup, go one step at a time and confirm each step before the next —
he is the builder but wants hands-on help with API/cloud/Python setup.**

---

## 11. Conventions

- **Language:** Python 3.10+. Official `anthropic` SDK. Match surrounding style; keep functions small.
- **Config over hardcoding:** model ID, BPM defaults, phase durations, paths → a single config module.
- **`.gitignore`** must cover `.env`, `credentials.json`, `*.db`, `recordings/`, `token.json`.
- **Commands** (fill in as the project is scaffolded):
  - Install: `pip install -r requirements.txt`
  - Run: `streamlit run app.py`
  - (Add test/lint commands once they exist.)
- **Tamil text:** keep UTF-8 throughout; verify rendering on Windows Chrome + Android Chrome.
- **When in doubt about pedagogy or persona, re-read §2 and §7 before §-anything-else.**
