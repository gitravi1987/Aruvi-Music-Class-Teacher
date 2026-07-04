"""Aruvi's Music Class — AI Carnatic teacher (MS Amma). Streamlit UI.

Run:  streamlit run app.py
v1 UI: music-themed, high-contrast, navigable. Live AI conversation + browser mic are
wired in next (marked with TODO on the Session screen).
"""
from __future__ import annotations

import base64
import mimetypes
from pathlib import Path

import streamlit as st

from core import db
from core.config import settings
from core.persona import GREETING, CLOSING
from core.session_manager import SessionManager, Phase

APP_NAME = "Aruvi's Music Class"

st.set_page_config(page_title=APP_NAME, page_icon="🎵", layout="wide")

# --- one-time init ---
if "initialized" not in st.session_state:
    db.init_db(seed=True)
    st.session_state.initialized = True
if "screen" not in st.session_state:
    st.session_state.screen = "Home"

# ---------------------------------------------------------------- theme / CSS
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Yatra+One&family=Tiro+Tamil:ital@0;1&family=Noto+Sans+Tamil:wght@400;600;700&display=swap');

      :root{
        --ivory:#FAF3E0; --cream:#F3E7C9; --gold:#D4A017; --brown:#8B4513;
        --lotus:#E8A0BF; --ink:#2C2C2C; --green:#4CAF50; --marigold:#FF9800;
      }

      .stApp{
        background:
          radial-gradient(circle at 10% 8%, rgba(212,160,23,.10), transparent 38%),
          radial-gradient(circle at 90% 0%, rgba(232,160,191,.12), transparent 42%),
          var(--ivory);
      }
      /* high contrast: dark text everywhere on the light background */
      .stApp, .stApp p, .stApp li, .stApp span, .stApp label, .stMarkdown{ color:var(--ink); }
      h1,h2,h3,h4{ font-family:'Tiro Tamil',serif; color:var(--brown) !important; }

      .app-title{ font-family:'Yatra One',cursive; color:var(--brown);
        font-size:1.5rem; line-height:1.2; }
      .app-tagline{ color:#7a5a2a; font-size:.8rem; margin-top:-2px; }
      .hero-title{ font-family:'Yatra One',cursive; color:var(--brown);
        font-size:2.5rem; margin:0; }
      .big{ font-size:21px; color:var(--ink); line-height:1.6; }

      /* buttons */
      .stButton>button{
        font-family:'Noto Sans Tamil',sans-serif; font-weight:700;
        background:linear-gradient(180deg,#edc24e,var(--gold));
        color:#3a2a06 !important; border:1px solid #b8860b; border-radius:14px;
        padding:.5rem .8rem; box-shadow:0 2px 6px rgba(139,69,19,.18);
        transition:transform .08s ease, box-shadow .15s ease;
      }
      .stButton>button:hover{ transform:translateY(-1px);
        box-shadow:0 5px 14px rgba(139,69,19,.30); border-color:var(--brown); }

      /* cards */
      .card{ background:rgba(255,255,255,.78); border:1px solid rgba(212,160,23,.5);
        border-radius:18px; padding:18px 22px; box-shadow:0 6px 18px rgba(139,69,19,.10);
        margin-bottom:14px; }
      .card h3{ margin-top:0; }

      /* avatar */
      .avatar-wrap{ text-align:center; }
      .avatar{ width:128px; height:128px; object-fit:cover; border-radius:50%;
        border:4px solid var(--gold); box-shadow:0 4px 14px rgba(139,69,19,.30);
        background:#fff; }
      .avatar.lg{ width:168px; height:168px; }
      .avatar-name{ font-family:'Tiro Tamil',serif; color:var(--brown);
        font-weight:700; margin-top:8px; font-size:1.1rem; }
      .avatar-sub{ color:#7a5a2a; font-size:.82rem; }

      /* sidebar header */
      .side-head{ text-align:center; padding:6px 0 10px;
        border-bottom:1px solid rgba(212,160,23,.4); margin-bottom:10px; }

      /* phase stepper */
      .stepper{ display:flex; gap:8px; flex-wrap:wrap; margin:4px 0 16px; }
      .step{ flex:1; min-width:110px; text-align:center; padding:10px 6px;
        border-radius:14px; border:1px solid rgba(212,160,23,.4);
        background:rgba(255,255,255,.6); color:#8a6a2a; font-size:.86rem; }
      .step.active{ background:linear-gradient(180deg,#f3d27a,var(--gold));
        color:#3a2a06; font-weight:700; border-color:var(--brown);
        box-shadow:0 4px 12px rgba(212,160,23,.4); }
      .step.done{ background:rgba(76,175,80,.16); color:#2f6f33;
        border-color:rgba(76,175,80,.5); }
      .step .ic{ font-size:1.5rem; display:block; }

      /* timer */
      .timer{ font-family:'Yatra One',cursive; font-size:2.6rem; color:var(--brown); }
      .paused-badge{ display:inline-block; background:var(--marigold); color:#fff;
        padding:3px 12px; border-radius:20px; font-weight:700; font-size:.8rem;
        vertical-align:middle; }

      /* lesson pills */
      .pill{ display:inline-block; padding:1px 9px; border-radius:20px;
        font-size:.72rem; margin-left:6px; }
      .pill.book{ background:rgba(139,69,19,.14); color:var(--brown); }
      .pill.syllabus{ background:rgba(232,160,191,.28); color:#9c3f6b; }

      /* floating notes (Home) */
      .notes{ position:relative; height:0; }
      .note{ position:absolute; font-size:1.5rem; opacity:.35; color:var(--gold);
        animation:floatup 7s ease-in infinite; }
      @keyframes floatup{ 0%{ transform:translateY(30px); opacity:0; }
        25%{ opacity:.55; } 100%{ transform:translateY(-130px); opacity:0; } }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- helpers
def img_uri(path) -> str | None:
    p = Path(path)
    if not p.exists():
        return None
    mime = mimetypes.guess_type(str(p))[0] or "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def amma_avatar():
    """Prefer a high-res illustrated portrait if dropped into assets/, else the photo."""
    for cand in (settings.assets_dir / "ms_amma.png",
                 settings.assets_dir / "ms_amma.jpg",
                 settings.ms_amma_avatar):
        if Path(cand).exists():
            return cand
    return None


PHASE_META = [
    (Phase.WARMUP, "🎵", "Warm-Up"),
    (Phase.HOMEWORK, "📝", "Homework"),
    (Phase.LESSON, "🎶", "Lesson"),
    (Phase.NEW, "✨", "New"),
    (Phase.WRAPUP, "🏠", "Wrap-Up"),
]


def stepper(sm: SessionManager):
    html = '<div class="stepper">'
    for idx, (_ph, ic, name) in enumerate(PHASE_META):
        cls = "step"
        if idx < sm.phase_index:
            cls += " done"
        elif idx == sm.phase_index:
            cls += " active"
        html += f'<div class="{cls}"><span class="ic">{ic}</span>{name}</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _render_timer(sm: SessionManager):
    secs = max(int(sm.elapsed_seconds()), 0)
    mm, ss = divmod(secs, 60)
    total = sm.total_minutes()
    badge = '<span class="paused-badge">⏸ PAUSED</span>' if sm.paused else ""
    st.markdown(f'<div class="timer">{mm:02d}:{ss:02d}&nbsp;{badge}</div>', unsafe_allow_html=True)
    st.progress(min(sm.elapsed_minutes() / total, 1.0) if total else 0.0)


# live-ticking timer when supported by this Streamlit version
_live_timer = st.fragment(run_every=1.0)(_render_timer) if hasattr(st, "fragment") else _render_timer


# ---------------------------------------------------------------- MS Amma live helpers
@st.cache_resource(show_spinner=False)
def get_amma():
    from core.pedagogy import MSAmma
    return MSAmma()


def speak_amma(text: str):
    """gTTS → mp3 bytes for playback in the browser. Returns bytes or None."""
    try:
        from core.tts import speak
        return Path(speak(text, lang="ta")).read_bytes()
    except Exception:
        return None


def clip_bytes(name: str):
    """Return (bytes, mime) for a pre-recorded human clip data/clips/<name>.<ext>, else (None, None)."""
    for ext, mime in {".mp3": "audio/mp3", ".wav": "audio/wav",
                      ".m4a": "audio/mp4", ".ogg": "audio/ogg"}.items():
        p = settings.clips_dir / f"{name}{ext}"
        if p.exists():
            return p.read_bytes(), mime
    return None, None


def amma_turn(sm: SessionManager, student_said: str | None = None, analysis: dict | None = None):
    """Call MS Amma with the current phase + context, append to chat history."""
    history = st.session_state.setdefault("chat", [])
    prior = [{"role": m["role"], "content": m["content"]} for m in history]
    conn = db.connect()
    lesson = db.current_lesson(conn)
    conn.close()
    phase_key = sm.phase.value if sm.phase is not Phase.DONE else "wrapup"
    reply = get_amma().respond(
        phase=phase_key,
        history=prior,
        student_said=student_said,
        analysis=analysis,
        lesson_name=lesson["lesson_name"] if lesson else None,
    )
    if student_said:
        history.append({"role": "user", "content": student_said})
    elif analysis:
        history.append({"role": "user", "content": "_🎵 (Aruvi sang for MS Amma)_"})
    history.append({"role": "assistant", "content": reply,
                    "audio": speak_amma(reply), "audio_fmt": "audio/mp3"})
    return reply


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown(
        f'<div class="side-head"><div class="app-title">🎵 {APP_NAME}</div>'
        f'<div class="app-tagline">Carnatic vocal lessons with MS Amma</div></div>',
        unsafe_allow_html=True,
    )
    uri = img_uri(amma_avatar())
    if uri:
        st.markdown(
            f'<div class="avatar-wrap"><img class="avatar" src="{uri}"/>'
            f'<div class="avatar-name">MS Amma</div>'
            f'<div class="avatar-sub">Paati Teacher · Carnatic Guru</div></div>',
            unsafe_allow_html=True,
        )
    st.write("")
    options = ["Home", "Session", "Progress", "Lessons", "Settings"]
    idx = options.index(st.session_state.screen) if st.session_state.screen in options else 0
    choice = st.radio("Menu", options, index=idx, label_visibility="collapsed")
    st.session_state.screen = choice
    st.caption(f"👧 {settings.student_name} · Curriculum Stage {settings.current_stage}")


# ---------------------------------------------------------------- screens
def home():
    notes = "".join(
        f'<span class="note" style="left:{x}%; animation-delay:{d}s">{n}</span>'
        for x, d, n in [(6, 0, "🎵"), (24, 1.6, "🎶"), (44, .7, "♪"),
                        (62, 2.3, "🎵"), (80, 1.1, "🎶"), (92, .3, "♪")]
    )
    st.markdown(f'<div class="notes">{notes}</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 2], gap="large")
    with left:
        uri = img_uri(amma_avatar())
        if uri:
            st.markdown(
                f'<div class="avatar-wrap"><img class="avatar lg" src="{uri}"/>'
                f'<div class="avatar-name">MS Amma</div>'
                f'<div class="avatar-sub">after Dr. M.S. Subbulakshmi</div></div>',
                unsafe_allow_html=True,
            )
    with right:
        st.markdown('<p class="hero-title">வணக்கம் அருவி! 🌸</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="card"><p class="big">{GREETING}</p></div>', unsafe_allow_html=True)

        conn = db.connect()
        lesson = db.current_lesson(conn)
        conn.close()
        if lesson:
            st.markdown(
                f'<div class="card"><h3>🎶 Today\'s lesson</h3>'
                f'<p class="big">{lesson["lesson_name"]}<br>'
                f'<span style="color:#7a5a2a">Raga {lesson["raga"]} · Tala {lesson["tala"]} · '
                f'Stage {lesson["stage"]}</span></p></div>',
                unsafe_allow_html=True,
            )
        if st.button("▶  Start today's class", type="primary", use_container_width=True):
            st.session_state.session = SessionManager()
            st.session_state.chat = []
            st.session_state.greeted = False
            st.session_state.screen = "Session"
            st.rerun()


def session_screen():
    sm: SessionManager | None = st.session_state.get("session")
    if sm is None:
        st.markdown('<p class="hero-title">🎶 Ready for class?</p>', unsafe_allow_html=True)
        st.markdown('<div class="card"><p class="big">No class is running yet, kanna.</p></div>',
                    unsafe_allow_html=True)
        if st.button("▶  Start today's class", type="primary"):
            st.session_state.session = SessionManager()
            st.session_state.chat = []
            st.session_state.greeted = False
            st.rerun()
        return

    st.markdown(f'<p class="hero-title">🎶 {sm.label}</p>', unsafe_allow_html=True)
    stepper(sm)

    try:
        _live_timer(sm)
    except Exception:
        _render_timer(sm)

    # MS Amma opens the class herself, warmly — once per class.
    if not st.session_state.get("greeted", False):
        gb, gfmt = clip_bytes("greeting")  # prefer the real human-recorded welcome
        if gb:
            st.session_state.setdefault("chat", []).append(
                {"role": "assistant", "content": GREETING, "audio": gb, "audio_fmt": gfmt})
        else:
            with st.spinner("MS Amma is getting ready to begin..."):
                try:
                    amma_turn(sm)
                except Exception:
                    st.session_state.setdefault("chat", []).append(
                        {"role": "assistant", "content": GREETING,
                         "audio": speak_amma(GREETING), "audio_fmt": "audio/mp3"})
        st.session_state.greeted = True
        st.rerun()

    if sm.break_due():
        st.success("🌟 Break time! Stretch and relax for 2 minutes, kanna.")
        if st.button("Resume after break"):
            sm.take_break()
            st.rerun()

    st.write("")
    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("⏮ Previous", use_container_width=True):
        sm.back()
        st.rerun()
    if c2.button("⏸ Pause", use_container_width=True, disabled=sm.paused):
        sm.pause()
        st.rerun()
    if c3.button("▶ Resume", use_container_width=True, disabled=not sm.paused):
        sm.resume()
        st.rerun()
    if c4.button("⏭ Next", use_container_width=True):
        sm.advance()
        st.rerun()
    if c5.button("🔄 Restart", use_container_width=True):
        st.session_state.session = SessionManager()
        st.session_state.chat = []
        st.session_state.greeted = False
        st.rerun()

    st.divider()
    st.markdown('<div class="card"><h3>🎙️ Sing or talk to MS Amma</h3></div>', unsafe_allow_html=True)

    if hasattr(st, "audio_input"):
        audio = st.audio_input("Tap the mic to record — sing a swara, or speak to MS Amma")
        if audio is not None:
            from datetime import datetime
            settings.recordings_dir.mkdir(parents=True, exist_ok=True)
            rec_path = settings.recordings_dir / f"rec_{datetime.now():%Y%m%d_%H%M%S}.wav"
            rec_path.write_bytes(audio.getvalue())
            st.caption(f"🎧 Recorded · saved as {rec_path.name}")
            a1, a2 = st.columns(2)
            if a1.button("🎵 I sang — MS Amma, listen", use_container_width=True):
                with st.spinner("MS Amma is listening to your singing..."):
                    try:
                        from core.pitch import analyze_singing
                        analysis = analyze_singing(rec_path)
                    except Exception:
                        analysis = {"summary": "I heard you sing, kanna!",
                                    "observations": [], "scores_are_advisory": True}
                    amma_turn(sm, analysis=analysis)
                st.rerun()
            if a2.button("💬 I spoke — MS Amma, reply", use_container_width=True):
                said = ""
                with st.spinner("MS Amma is listening... (first time loads the model)"):
                    try:
                        from core.transcribe import transcribe
                        said = transcribe(rec_path)
                    except Exception:
                        said = ""
                    if said:
                        amma_turn(sm, student_said=said)
                if said:
                    st.rerun()
                else:
                    st.warning("I couldn't catch the words clearly — please type below instead.")
    else:
        st.info("This Streamlit version has no in-browser recorder — use the text box below.")

    typed = st.text_input("Or type a message to MS Amma", key="typed_msg")
    if st.button("Send 💬") and typed.strip():
        with st.spinner("MS Amma is thinking..."):
            amma_turn(sm, student_said=typed.strip())
        st.rerun()

    for m in st.session_state.get("chat", []):
        role = "assistant" if m["role"] == "assistant" else "user"
        with st.chat_message(role, avatar="🪕" if role == "assistant" else "👧"):
            st.markdown(m["content"])
            if m.get("audio"):
                st.audio(m["audio"], format=m.get("audio_fmt", "audio/mp3"))

    if sm.phase is Phase.WRAPUP or sm.phase is Phase.DONE:
        st.markdown(f'<div class="card"><p class="big">{CLOSING}</p></div>', unsafe_allow_html=True)
        cb, cfmt = clip_bytes("closing")  # prefer the real human-recorded blessing
        if cb:
            st.audio(cb, format=cfmt)


def progress_screen():
    st.markdown('<p class="hero-title">📈 Aruvi\'s Progress</p>', unsafe_allow_html=True)
    conn = db.connect()
    rows = conn.execute("SELECT * FROM session_log ORDER BY date").fetchall()
    conn.close()
    if not rows:
        st.markdown('<div class="card"><p class="big">No sessions logged yet — '
                    'progress charts appear here after the first class.</p></div>',
                    unsafe_allow_html=True)
        return
    st.line_chart({"overall": [r["overall_score"] or 0 for r in rows]})


def lessons_screen():
    st.markdown('<p class="hero-title">📚 Lessons</p>', unsafe_allow_html=True)
    st.caption("Ganamrudha Bodhini + MS Amma's syllabus.  🔒 locked · 🎵 in progress · ⭐ mastered")
    conn = db.connect()
    rows = conn.execute("SELECT * FROM lessons ORDER BY stage, track, lesson_number").fetchall()
    conn.close()
    icon = {"locked": "🔒", "in_progress": "🎵", "mastered": "⭐"}
    current_stage = None
    for r in rows:
        if r["stage"] != current_stage:
            current_stage = r["stage"]
            st.markdown(f"### Stage {current_stage}")
        meta = " · ".join(b for b in [f"Track {r['track']}", r["raga"], r["tala"]] if b)
        pill = f'<span class="pill {r["source"]}">{r["source"]}</span>' if r["source"] else ""
        st.markdown(
            f'<div class="card" style="padding:10px 16px;margin-bottom:8px;">'
            f'{icon.get(r["status"], "")} <b>{r["lesson_name"]}</b>{pill}<br>'
            f'<span style="color:#7a5a2a;font-size:.9rem">{meta}</span></div>',
            unsafe_allow_html=True,
        )


def settings_screen():
    st.markdown('<p class="hero-title">⚙️ Settings</p>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="card"><p class="big">'
        f'<b>Pedagogy model:</b> {settings.model}<br>'
        f'<b>Report emails:</b> {", ".join(settings.parent_emails)}<br>'
        f'<b>Session length:</b> {settings.total_minutes()} min (phases: {settings.phase_minutes})'
        f'</p></div>', unsafe_allow_html=True)
    if settings.anthropic_api_key:
        st.success("Anthropic API key detected ✓")
    else:
        st.error("ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.")
    if not img_uri(amma_avatar()):
        st.warning("MS Amma avatar image not found.")
    else:
        st.caption("Tip: drop a high-res illustrated portrait at assets/ms_amma.png to upgrade the avatar.")
    st.caption("The API key is read from .env — never entered or stored in the UI (privacy).")


PAGES = {
    "Home": home,
    "Session": session_screen,
    "Progress": progress_screen,
    "Lessons": lessons_screen,
    "Settings": settings_screen,
}
PAGES[st.session_state.screen]()
