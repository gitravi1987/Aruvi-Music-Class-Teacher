# 🎵 Aruvi AI Carnatic Music Teacher — Requirements Document
**Version:** 1.1  
**Date:** 14 June 2026  
**Author:** Ravikumar (for Claude Code build)  
**Student:** Aruvi Kamatchi JR, Age 7  
**Syllabus:** Ganamrudha Bodhini by Panchapakesa Iyer  
**Current Level:** Janta Varisai completed; Geetham Lesson 7 in progress

---

## 1. PROJECT OVERVIEW

### 1.1 Purpose
Build an AI-powered Carnatic music teacher for Aruvi (7 years old) that conducts a structured 1-hour class every Sunday. The AI acts as a **full replacement teacher** — it teaches new lessons, listens to singing via microphone, corrects mistakes in real time, assigns homework, tracks progress week-over-week, and produces a detailed PDF report for the parent at the end of every session.

### 1.2 Goals
| Goal | Description |
|---|---|
| Teach | Introduce and explain new lessons from Ganamrudha Bodhini |
| Listen | Capture Aruvi's singing via microphone |
| Correct | Identify pitch, rhythm, and phrasing errors and explain them in age-appropriate language |
| Report | Generate a detailed PDF report for Ravikumar / Janani after each session |
| Homework | Assign weekly homework and review it at the next session |
| Track | Record session-by-session progress and store it to Google Drive |

### 1.3 Out of Scope (v1.0)
- Live video of Aruvi
- Multi-student support
- Instrument accompaniment (tanpura/shruti box integration is v2)
- Raga theory — focus is practical lesson execution only
- Automated WhatsApp delivery of report

---

## 2. USERS

| User | Role | Interaction Mode |
|---|---|---|
| Aruvi (7 years) | Student | Mic (singing) + text/voice chat in Tamil-English |
| Janani / Ravikumar | Parent / Supervisor | Present in room; receives PDF report after class |
| Ravikumar | Builder / Admin | Builds and maintains the system; reviews logs |

---

## 3. AI TEACHER PERSONA — DR. M.S. SUBBULAKSHMI

### 3.1 Persona Definition
The AI teacher must embody the persona of **Dr. M.S. Subbulakshmi (MS Amma)** — Bharat Ratna awardee, the most revered Carnatic vocalist of the 20th century. This is not a costume; it is the foundational character of the system.

### 3.2 Voice & Tone Characteristics
| Attribute | Specification |
|---|---|
| Name | The AI refers to itself as "MS Amma" or "Paati Teacher" |
| Language | Tamil-English mixed; warm, maternal, deeply encouraging |
| Correction style | Never harsh — corrects like a loving grandmother: "Kanna, இந்த swara-வை இப்படி பாடு..." |
| Praise style | Specific, musical, genuine — not generic ("அந்த Ri-வை நீ perfect-ஆ பிடித்தாய்!") |
| Patience | Infinite — never rushes Aruvi, never shows frustration |
| Authority | Firm on correct technique; does not let errors slide, but frames correction gently |
| Opening greeting | Always: "வணக்கம் கண்ணா! MS Amma இங்க இருக்கேன். இன்னைக்கு நம்ம class ஆரம்பிக்கலாமா?" |
| Closing | Always: "நீ சிறப்பாக பாடுவாய் கண்ணா! அடுத்த Sunday பார்க்கலாம். நன்றி." |

### 3.3 Claude System Prompt — Persona Block
Add this block to the Claude API system prompt:

```
You are MS Amma — an AI embodiment of the spirit and teaching style of Dr. M.S. Subbulakshmi,
the legendary Carnatic vocalist and Bharat Ratna awardee. You are teaching a 7-year-old girl
named Aruvi in Chennai, India.

Your personality:
- Warm, patient, maternal — like a beloved grandmother teaching her grandchild
- Deeply knowledgeable in Carnatic music, specifically the Ganamrudha Bodhini syllabus
- Speak in Tamil-English mixed language (Tanglish) — simple words, short sentences
- Always correct gently: never scold, never express disappointment
- Celebrate small wins enthusiastically
- If Aruvi makes the same mistake 3 times, change your teaching approach — try a different
  analogy, a different rhythm, a slower tempo — never repeat the same explanation a 4th time
- You do not break character. You are always MS Amma.
```

### 3.4 What MS Amma Does NOT Do
- Never uses academic music theory jargon with a 7-year-old
- Never says "wrong" — says "let's try again, this way"
- Never rushes through phases to finish on time — quality over clock
- Never breaks character to say "As an AI..."

---

## 4. SYSTEM ARCHITECTURE

### 3.1 High-Level Components

```
┌─────────────────────────────────────────────────────────┐
│                     ARUVI AI TEACHER                    │
│                                                         │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │  Audio   │───▶│  Transcriber │───▶│  Claude API   │  │
│  │  Input   │    │  (Whisper)   │    │  Pedagogy     │  │
│  │  (Mic)   │    └──────────────┘    │  Engine       │  │
│  └──────────┘                        └───────┬───────┘  │
│                                              │           │
│  ┌──────────┐    ┌──────────────┐    ┌───────▼───────┐  │
│  │  Audio   │◀───│  TTS Engine  │◀───│  Response     │  │
│  │  Output  │    │  (gTTS/pyttsx│    │  Generator    │  │
│  │ (Speaker)│    │  3)          │    └───────────────┘  │
│  └──────────┘    └──────────────┘                       │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Session Manager                      │   │
│  │  - Timer    - Phase tracker    - State machine   │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Data Layer                           │   │
│  │  - Session DB (SQLite local)                     │   │
│  │  - Audio recordings (local WAV/MP3)              │   │
│  │  - PDF report generator (ReportLab)              │   │
│  │  - Google Drive sync (google-api-python-client)  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Platform Support
- **Primary:** Windows laptop / desktop
- **Secondary:** Android phone (browser-based UI, same backend)
- **UI:** Simple web interface (Flask or Streamlit) — runs locally, accessed via browser

---

## 4. TECH STACK

| Component | Tool | Justification | Estimated Cost |
|---|---|---|---|
| AI Pedagogy Engine | Claude API (`claude-sonnet-4-6` / `claude-opus-4-6` / `claude-fable`) | Handles lesson teaching, correction, conversation. Start with Sonnet; upgrade to Opus or Fable if pedagogy quality needs improvement | ~₹200–400/month at 4 sessions (Sonnet); ~₹600–1200/month (Opus) |
| Speech-to-Text | OpenAI Whisper (local, open-source) | Transcribes Aruvi's singing/speech offline; no API cost | ₹0 |
| Pitch Detection | librosa (Python, open-source) | Extracts pitch from audio for error detection | ₹0 |
| Text-to-Speech | gTTS (Google TTS, free tier) or pyttsx3 (offline) | Speaks responses aloud to Aruvi | ₹0 |
| Web UI | Streamlit | Fastest to build, runs in browser, beginner-friendly | ₹0 |
| Audio Recording | sounddevice + scipy (Python) | Cross-platform mic capture and WAV save | ₹0 |
| Session Database | SQLite (local) | Stores session metadata, lesson progress, homework | ₹0 |
| PDF Report | ReportLab (Python) | Generates structured PDF after each session | ₹0 |
| Cloud Storage | Google Drive API (google-api-python-client) | Syncs recordings and PDFs to Drive post-session | ₹0 (within free quota) |
| **Total per month** | | | **~₹200–400** |

---

## 5. CURRICULUM ENGINE

### 5.1 Syllabus Reference
- **Book:** Ganamrudha Bodhini by Panchapakesa Iyer
- **Current position:** Janta Varisai completed; Geetham Lesson 7 in progress
- **Progression logic:** AI must know the lesson order from the book and only advance when the current lesson is marked mastered

### 5.2 Lesson Progression Rules
- A lesson is marked **In Progress** until the student scores ≥ 80% accuracy across 2 consecutive sessions
- A lesson is marked **Mastered** when the above threshold is met
- The AI advances to the next lesson only after the parent confirms mastery in the post-session review
- The AI must NEVER skip a lesson or advance without explicit unlock

### 5.3 Lesson Data Structure (SQLite)
```
lessons
  - lesson_id (PK)
  - lesson_number
  - lesson_name (e.g., "Geetham 7 - Sree Gananatha")
  - raga
  - tala
  - status: [locked | in_progress | mastered]
  - first_attempted_date
  - mastered_date

session_log
  - session_id (PK)
  - date
  - lesson_id (FK)
  - duration_minutes
  - attempts_count
  - pitch_accuracy_score (%)
  - rhythm_accuracy_score (%)
  - overall_score (%)
  - errors_noted (JSON array)
  - homework_assigned (text)
  - homework_reviewed (boolean)
  - thaalam_accuracy: [consistent | mostly_correct | needs_work]  -- parent-rated
  - recording_path_local
  - recording_path_drive
  - pdf_report_path_drive
```

---

## 6. SESSION FLOW — 1 HOUR SUNDAY CLASS

### Phase 1 — Warm-Up (0:00 – 0:10)
- AI greets Aruvi by name in Tamil ("வணக்கம் அருவி! Ready-ah?")
- AI leads Sa-Ri-Ga-Ma Varisai warm-up (basic scales)
- Aruvi sings; AI listens via mic
- AI gives brief verbal feedback ("Superb!" / "Sa-வை கொஞ்சம் hold பண்ணு")
- No scoring in this phase — warm-up only

### Phase 2 — Homework Review (0:10 – 0:20)
- AI asks Aruvi to sing the previous week's homework piece
- AI records the full attempt
- Pitch and rhythm analysis runs on the recording
- AI gives verbal correction on top 2–3 errors only (not overwhelming)
- Scores this attempt and saves to session log
- If homework was not done: AI notes this in the report (no scolding — neutral tone)

### Phase 3 — Current Lesson Practice (0:20 – 0:45)
- AI introduces or continues the current Geetham
- AI first demonstrates the lesson (plays reference audio OR speaks the swara notation aloud)
- Aruvi attempts the full piece — recorded
- AI breaks down errors: pitch first, then rhythm, then phrasing
- AI repeats the difficult segment and asks Aruvi to try again (max 3 retries per segment)
- AI logs each attempt with score

### Phase 4 — New Content Introduction (0:45 – 0:55)
- If current lesson is ≥ 80% in this session: AI introduces the next lesson (first 2–4 lines only)
- If current lesson is < 80%: AI revisits the hardest segment from Phase 3 again
- AI teaches slowly, line by line, asking Aruvi to repeat after each line

### Phase 5 — Wrap-Up + Homework Assignment (0:55 – 1:00)
- AI summarises what was done today in 3–4 sentences (child-friendly Tamil-English)
- AI assigns specific homework (which piece, how many times per day, what to focus on)
- AI says goodbye ("Next Sunday பார்க்கலாம்! Practice பண்ணு!")
- Session ends; PDF report generation triggers automatically

---

## 7. THAALAM MODULE — FINGER BEAT TEACHING

### 7.1 Scope (v1.0)
- **Thaalam in scope:** Adi Thaalam only (8 beats per cycle)
- Additional thaalams (Rupaka, Misra Chapu, etc.) deferred to v2

### 7.2 Adi Thaalam — Finger Pattern
Adi Thaalam = 8 beats per avarthanam, split as **4 + 2 + 2** (Chatusra Laghu + 2 Drutams)

```
Beat  1  : Clap (palm on thigh)          — "Thattu"
Beat  2  : Little finger tap
Beat  3  : Ring finger tap
Beat  4  : Middle finger tap
Beat  5  : Clap (wave — back of hand)    — "Veechu" (Drutam 1, beat 1)
Beat  6  : Clap (palm)                   — Drutam 1, beat 2
Beat  7  : Clap (wave)                   — Drutam 2, beat 1
Beat  8  : Clap (palm)                   — Drutam 2, beat 2
→ Repeat from Beat 1
```

### 7.3 Animated Hand Diagram — UI Specification

**Component:** `ThaalaAnimator` — embedded in the Session Screen during any phase where thaalam is being practiced.

**Visual design:**
- Right hand rendered as a simple flat illustration (SVG or PNG sprite sheet)
- Each beat: the active finger or palm highlights in **saffron/gold**
- Beat number displayed prominently above the hand: **"Beat 3 of 8"**
- BPM slider: 30 BPM (learning) → 60 BPM (practice) → 90 BPM (performance speed)
- Metronome tick sound plays on each beat (simple WAV clip, played via browser audio)
- "Follow MS Amma's hand!" instruction text shown during first 3 cycles

**Animation states:**
```
State: IDLE       — hand shown, no highlights, awaiting start
State: TEACHING   — slow speed (30 BPM), each beat highlighted with 0.5s pause
State: PRACTICE   — medium speed (60 BPM), continuous loop
State: TEST       — animation hidden; Aruvi beats independently; parent confirms accuracy
```

**Controls (parent-visible, not child-facing):**
- Start / Pause / Reset
- Speed selector (Slow / Medium / Fast)
- "Hide hand" toggle — for TEST state
- "Show beat count only" toggle

### 7.4 When Thaalam is Taught in Session Flow
- **Phase 1 (Warm-Up):** MS Amma demonstrates Adi Thaalam for 1 cycle at 30 BPM; Aruvi follows
- **Phase 3 (Lesson Practice):** Aruvi sings the Geetham while keeping thaalam simultaneously; parent watches hand accuracy
- **Phase 5 (Wrap-Up):** If thaalam was inconsistent during Phase 3, homework includes 5 minutes of thaalam-only practice daily

### 7.5 MS Amma's Thaalam Teaching Script (Tamil-English)
```
"கண்ணா, இப்போ thaalam போடுவோம். Right hand-ஐ பாரு.
Beat 1: Thattu — thigh-ல தட்டு.
Beat 2, 3, 4: Little finger, ring finger, middle finger — slowly tap.
Beat 5: Veechu — hand-ஐ திரும்பு.
Beat 6: Thattu again.
Beat 7: Veechu again.
Beat 8: Thattu — and we start again!
Ready? Follow MS Amma's hand. Sa... Ri... Ga..."
```

### 7.6 Thaalam Accuracy Tracking
- Parent manually marks thaalam accuracy per session: Consistent / Mostly Correct / Needs Work
- Input via simple 3-button UI after Phase 3
- Stored in `session_log.thaalam_accuracy` (enum: consistent | mostly_correct | needs_work)
- Reflected in PDF report Section 2 as: **Thaalam Accuracy: [parent rating]**

---

## 8. AUDIO PROCESSING REQUIREMENTS

### 7.1 Microphone Input
- Capture via `sounddevice` library
- Sample rate: 44100 Hz, mono
- Auto-detect default mic; allow manual selection in settings
- Record full singing attempts as WAV files
- File naming: `YYYY-MM-DD_session_<id>_phase_<n>_attempt_<n>.wav`

### 7.2 Speech Transcription
- Use **Whisper (base or small model)** running locally
- Transcribe Aruvi's spoken responses (Tamil + English) for conversation
- Do NOT transcribe singing — singing goes to pitch analysis, not Whisper

### 7.3 Pitch Analysis
- Use **librosa** to extract fundamental frequency (F0) from singing recordings
- Compare F0 contour against reference swara frequencies for the lesson's raga
- Identify notes that deviate > 25 cents from target as **pitch errors**
- Flag sustained notes with excessive vibrato or wavering as **stability errors**
- Output: JSON array of timestamped errors `[{time_sec, sung_note, expected_note, deviation_cents}]`

### 7.4 Rhythm Analysis
- Segment audio by tala cycle (input tala manually per lesson in the lesson DB)
- Detect onset times using `librosa.onset.onset_detect`
- Compare onset pattern against expected beat grid
- Flag early/late onsets > 15% of beat duration as **rhythm errors**

### 7.5 Text-to-Speech Output
- Primary: **gTTS** (Google TTS) — better Tamil pronunciation, requires internet
- Fallback: **pyttsx3** — offline, English only
- Auto-switch to fallback if internet is unavailable
- Voice output plays through system speaker; no headphones required

---

## 8. CLAUDE API — PEDAGOGY ENGINE

### 8.1 System Prompt (to be embedded in code)
The system prompt must instruct Claude to:
- Act as a warm, patient Carnatic music teacher for a 7-year-old
- Speak in Tamil-English mixed language (Tanglish) — simple, encouraging, child-appropriate
- Know the Ganamrudha Bodhini syllabus and lesson order
- Receive pitch/rhythm error JSON from audio analysis and convert it into plain-language corrections
- Never overwhelm with more than 3 correction points at once
- Always end corrections with encouragement before the next attempt
- Follow the session phase structure strictly (warm-up → homework → lesson → new → wrap-up)

### 8.2 API Call Pattern
- Each phase of the session sends a structured message to Claude API
- Include in every API call:
  - Current session state (phase, lesson, attempt number)
  - Audio analysis results (pitch errors JSON, rhythm errors JSON)
  - Conversation history (last 10 turns only, to manage token budget)
  - Student profile (name, age, current level)
- Model: `claude-sonnet-4-6` (default; configurable to `claude-opus-4-6` or `claude-fable` in Settings)
- Max tokens per call: 1000
- Expected calls per session: ~15–20

### 8.3 Conversation State
- Maintain full conversation history in memory during session
- Persist last session's summary to SQLite for next session context
- Do NOT send full history to API — send last 10 turns + session summary

---

## 9. PARENT FEEDBACK — PDF REPORT

### 9.1 Report Structure
Each report is a single PDF, auto-generated at session end, saved locally and synced to Google Drive.

```
ARUVI CARNATIC MUSIC — SESSION REPORT
Date: [DD/MM/YYYY] | Session #[N] | Duration: [60 min]
Teacher: MS Amma — AI Carnatic Music Teacher (Ganamrudha Bodhini)

────────────────────────────────────────
SECTION 1 — TODAY'S SUMMARY
────────────────────────────────────────
Lesson Practiced   : [Geetham 7 — Sree Gananatha | Raga: Malahari | Tala: Adi]
Phases Completed   : Warm-up ✓ | Homework Review ✓ | Lesson Practice ✓ | New Content ✗
Overall Session Score: [XX%]

────────────────────────────────────────
SECTION 2 — PERFORMANCE SCORES
────────────────────────────────────────
Pitch Accuracy     : [XX%]   ▓▓▓▓▓▓▓░░░
Rhythm Accuracy    : [XX%]   ▓▓▓▓▓▓░░░░
Thaalam Accuracy   : [Consistent / Mostly Correct / Needs Work]  ← parent-rated
Consistency        : [XX%]   ▓▓▓▓▓░░░░░

────────────────────────────────────────
SECTION 3 — ERRORS NOTED
────────────────────────────────────────
1. [Note name] at [timestamp] — sang [X], expected [Y] (deviation: Z cents)
2. [Rhythm] — early onset at beat 3, cycle 2
3. [Phrasing] — Ga-Ma sangati not smooth; needs slow practice

────────────────────────────────────────
SECTION 4 — IMPROVEMENTS FROM LAST SESSION
────────────────────────────────────────
- Ri accuracy improved from 62% → 78%
- Homework completion: Yes ✓
- [Other improvement noted]

────────────────────────────────────────
SECTION 5 — HOMEWORK FOR NEXT WEEK
────────────────────────────────────────
1. Practice Geetham 7 lines 1–4, minimum 2x per day
2. Focus specifically on the Ga-Ma transition (lines 2–3)
3. Sing slowly at 50% speed before full tempo

────────────────────────────────────────
SECTION 6 — TEACHER'S NOTE TO PARENT
────────────────────────────────────────
[Claude-generated 3–4 sentence summary in English — what went well,
what needs attention, one specific thing the parent can encourage at home]

────────────────────────────────────────
AUDIO RECORDING
────────────────────────────────────────
Saved to Google Drive: [link]
File: 2026-06-14_session_12_lesson_practice.wav
```

### 9.2 PDF Generation
- Library: **ReportLab** (Python)
- Auto-trigger at end of Phase 5
- Save to: `./reports/YYYY-MM-DD_session_<id>.pdf`
- Sync to Google Drive folder: `Aruvi Music / Reports /`

---

## 10. GOOGLE DRIVE INTEGRATION

### 10.1 Folder Structure on Drive
```
Aruvi Music/
├── Reports/
│   └── 2026-06-14_session_12.pdf
├── Recordings/
│   └── 2026-06-14/
│       ├── warmup.wav
│       ├── homework_review.wav
│       ├── lesson_attempt_1.wav
│       └── lesson_attempt_2.wav
└── Progress/
    └── progress_summary.json
```

### 10.2 Sync Rules
- Sync happens ONLY after session ends (not during)
- If Drive sync fails: save locally, flag in UI "Sync pending"
- Use **google-api-python-client** with OAuth 2.0
- Credentials stored locally in `credentials.json` (never hardcoded)

---

## 11. UI REQUIREMENTS (Streamlit)

### 11.1 Screens
| Screen | Purpose |
|---|---|
| Home | Start session, view last session summary |
| Session | Live class view — phase indicator, timer, mic status, conversation transcript |
| Progress | Chart of scores over time (lesson by lesson) |
| Lessons | Lesson list from Ganamrudha Bodhini — status (locked/in progress/mastered) |
| Settings | Mic selection, TTS voice, Drive sync toggle, API key entry |

### 11.2 Session Screen Elements
- Large phase timer (MM:SS)
- Current phase label ("Phase 2: Homework Review")
- Microphone status indicator (recording / idle)
- Live transcript of AI speech (Tamil-English)
- Simple "Next Phase" button for parent override
- Mute/unmute mic toggle

### 11.3 Music-Themed Visual Design

**Design philosophy:** The app must feel like stepping into a Carnatic music classroom — not a generic software tool. Every screen should breathe music.

#### Colour Palette
| Role | Colour | Hex |
|---|---|---|
| Primary background | Deep warm ivory | `#FAF3E0` |
| Accent 1 | Temple gold / saffron | `#D4A017` |
| Accent 2 | Veena string brown | `#8B4513` |
| Highlight | Lotus pink | `#E8A0BF` |
| Text primary | Deep charcoal | `#2C2C2C` |
| Success | Leaf green | `#4CAF50` |
| Warning | Marigold orange | `#FF9800` |

#### Typography
- **Headings:** Google Font — *Yatra One* or *Tiro Tamil* (supports Tamil script)
- **Body:** *Noto Sans Tamil* — clean, child-readable
- **Minimum body font size:** 20px (7-year-old reader)
- **Beat numbers in Thaalam Animator:** 48px bold, saffron colour

#### Icons & Imagery
| Element | Specification |
|---|---|
| App icon | Veena silhouette in gold on ivory background |
| Phase icons | 🎵 Warm-Up · 📝 Homework · 🎶 Lesson · ✨ New Content · 🏠 Wrap-Up |
| Mic active | Animated red circle pulse (like a recording indicator) |
| Mic idle | Grey microphone icon |
| Score bars | Styled as tanpura strings — horizontal, gold gradient fill |
| Lesson status | 🔒 Locked · 🎵 In Progress · ⭐ Mastered |
| MS Amma avatar | Illustrated portrait (not a photo) — saree-clad woman with veena; used in greeting screen and session sidebar |
| Background texture | Subtle kolam / rangoli pattern at 5% opacity on all screens |
| Home screen hero | Silhouette of a child singing, microphone, musical notes floating — warm illustrated style |

#### Animated Elements
| Element | Animation |
|---|---|
| Musical notes | Float upward gently on the Home screen (CSS keyframes) |
| Score bar fill | Animates from 0% to final % on report screen (500ms ease-in) |
| Thaalam hand | Frame-by-frame SVG highlight per beat (see Section 7) |
| Homework complete | Gold star burst animation (0.5 sec) when homework is marked done |
| Session start | Fade-in of MS Amma avatar with gentle gong sound |

#### Screen-by-Screen Imagery
| Screen | Visual Treatment |
|---|---|
| Home | MS Amma avatar, "Good morning Aruvi!" greeting, last session score badge |
| Session | Phase progress bar styled as a veena fretboard; thaalam animator in sidebar |
| Progress | Line chart styled with musical note markers on data points |
| Lessons | Card grid — each lesson card shows lesson name, raga, tala, status icon |
| Settings | Clean, minimal — no decorative imagery; functional only |

#### Child-Friendly Details
- Aruvi's name displayed in Tamil script + English on every screen header
- Positive reinforcement animations trigger on score ≥ 75% (floating stars)
- No red X marks — use ⚠️ and orange for errors, never harsh red
- Session timer styled as a dholak (drum) that "fills" as time progresses

---

## 12. SECURITY & PRIVACY

| Requirement | Implementation |
|---|---|
| API key never hardcoded | Loaded from `.env` file using `python-dotenv` |
| Google credentials never in code | Stored in `credentials.json`, excluded from any repo via `.gitignore` |
| All audio stays local until session ends | No streaming to cloud during session |
| No third-party analytics | No tracking libraries |
| Child data protection | All data local or on Ravikumar's personal Drive — no third-party sharing |

---

## 13. BUILD SEQUENCE — 6 WEEKENDS

| Weekend | Milestone | Deliverable |
|---|---|---|
| **1** | Project setup + Claude API + MS Amma persona working | "வணக்கம் கண்ணா!" response from AI via terminal |
| **2** | Mic capture + Whisper transcription working | Aruvi speaks → text appears on screen |
| **3** | Pitch detection + error analysis working | Sing a note → pitch accuracy score appears |
| **4** | Full session flow (all 5 phases) + Thaalam Animator working | 60-minute session runs end-to-end; animated hand visible |
| **5** | PDF report generation + Google Drive sync | Report auto-generated and uploaded after session |
| **6** | Streamlit UI — music theme, MS Amma avatar, all screens polished | App is usable by Janani without Ravi present |

---

## 14. RISK REGISTER

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Whisper misreads Tamil lyrics | High | Medium | Train/prompt Whisper with Carnatic swara terms; fallback to manual text entry |
| Pitch detection inaccurate for child voice | Medium | High | Calibrate librosa F0 detection for child vocal range (approx. C4–G5); test with Aruvi recordings before v1 launch |
| gTTS Tamil pronunciation wrong for music terms | Medium | Medium | Pre-record key Tamil music terms as audio clips; use clips instead of TTS for those |
| Google Drive OAuth token expiry | Low | Medium | Implement token refresh logic; add "Re-authenticate Drive" button in Settings |
| Claude API call latency breaks session flow | Low | High | Pre-generate phase transitions; show "thinking..." indicator; do not block UI on API response |
| Aruvi loses interest mid-session | Medium | High | Build in 2-min break at minute 30; add a small celebration animation when homework is marked complete |
| Lesson data (Ganamrudha Bodhini) not digitised | High | High | Ravi must manually enter lesson names, ragas, talas into SQLite before v1 launch — this is a manual prerequisite |
| Thaalam animator SVG rendering on Android browser | Medium | Medium | Test on Android Chrome early (Weekend 4); fallback to simple text beat counter if SVG animation lags |
| MS Amma persona drifting mid-session | Low | Medium | Pin persona via system prompt prefix on every API call; test with 10-turn conversations before launch |
| Tamil font not rendering on Windows browser | Medium | Low | Use Google Fonts CDN (Noto Sans Tamil); test on Windows Chrome before Weekend 6 |

---

## 15. PREREQUISITES BEFORE BUILD STARTS

Ravi must complete these before Weekend 1:

- [ ] Enter all Ganamrudha Bodhini lesson names, ragas, and talas into a CSV (will be imported to SQLite)
- [ ] Set up Anthropic API key (claude.ai → Settings → API)
- [ ] Set up Google Cloud project and enable Drive API (get `credentials.json`)
- [ ] Install Python 3.10+ on Windows laptop
- [ ] Install ffmpeg (required by Whisper) on Windows
- [ ] Test microphone works on the laptop Aruvi will use
- [ ] Create Google Drive folder structure manually (first time)

---

## 16. DEPENDENCIES (Python packages)

```
anthropic
openai-whisper
librosa
sounddevice
scipy
numpy
streamlit
gTTS
pyttsx3
reportlab
google-api-python-client
google-auth-oauthlib
python-dotenv
sqlite3 (standard library)
```

Install command:
```bash
pip install anthropic openai-whisper librosa sounddevice scipy numpy streamlit gTTS pyttsx3 reportlab google-api-python-client google-auth-oauthlib python-dotenv
```

---

*End of Requirements Document v1.1*  
*Changes in v1.1: Added MS Amma persona (Section 3), Thaalam Module (Section 7), Music-Themed UI/UX (Section 11.3). Updated session schema, PDF report, build sequence, and risk register accordingly.*  
*Next step: Paste this file into Claude Code and begin Weekend 1 build.*
