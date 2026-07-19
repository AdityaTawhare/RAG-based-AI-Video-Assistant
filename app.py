import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
import time
import datetime
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Mega CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ── Root Variables ── */
:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface-2: #1a1a25;
    --surface-3: #22223a;
    --border: #2a2a3a;
    --border-hover: #4a4a6a;
    --accent: #7c3aed;
    --accent-glow: #9f67ff;
    --accent-2: #06b6d4;
    --accent-3: #f472b6;
    --text: #e8e8f0;
    --text-muted: #7070a0;
    --text-dim: #50507a;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
}

/* Animated grid background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(124, 58, 237, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(124, 58, 237, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* ── Floating Orbs ── */
.orb-container {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.12;
    animation: orbFloat 20s ease-in-out infinite;
}

.orb-1 {
    width: 400px; height: 400px;
    background: var(--accent);
    top: 10%; left: -5%;
    animation-delay: 0s;
}

.orb-2 {
    width: 300px; height: 300px;
    background: var(--accent-2);
    top: 60%; right: -5%;
    animation-delay: -7s;
    animation-duration: 25s;
}

.orb-3 {
    width: 250px; height: 250px;
    background: var(--accent-3);
    bottom: 10%; left: 40%;
    animation-delay: -13s;
    animation-duration: 30s;
}

@keyframes orbFloat {
    0%, 100% { transform: translate(0, 0) scale(1); }
    25% { transform: translate(40px, -30px) scale(1.1); }
    50% { transform: translate(-20px, 20px) scale(0.95); }
    75% { transform: translate(30px, 40px) scale(1.05); }
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* ── Headings ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
}

/* ── Hero Title ── */
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800;
    line-height: 1.1;
    margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent-glow) 50%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: heroGlow 4s ease-in-out infinite alternate;
}

@keyframes heroGlow {
    0% { filter: brightness(1); }
    100% { filter: brightness(1.2); }
}

.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: cardFadeIn 0.5s ease-out both;
}

.card:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(124, 58, 237, 0.15);
}

.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--accent), var(--accent-2));
    transition: width 0.3s;
}

.card:hover::before {
    width: 5px;
}

@keyframes cardFadeIn {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-content {
    font-size: 0.875rem;
    line-height: 1.7;
    color: var(--text);
}

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.badge-purple { background: rgba(124,58,237,0.2); color: var(--accent-glow); border: 1px solid rgba(124,58,237,0.3); }
.badge-cyan   { background: rgba(6,182,212,0.15); color: var(--accent-2);    border: 1px solid rgba(6,182,212,0.3); }
.badge-green  { background: rgba(16,185,129,0.15); color: var(--success);    border: 1px solid rgba(16,185,129,0.3); }
.badge-pink   { background: rgba(244,114,182,0.15); color: var(--accent-3);  border: 1px solid rgba(244,114,182,0.3); }

/* ── Input & Buttons ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    transition: all 0.3s !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.2) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent), #5b21b6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-transform: uppercase !important;
    position: relative !important;
    overflow: hidden !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(124,58,237,0.5) !important;
}

.stButton > button:active {
    transform: translateY(0px) scale(0.98) !important;
}

/* ── Progress Pipeline ── */
.pipeline-container {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    margin: 0.5rem 0;
}

.pipeline-step {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 0.85rem;
    background: var(--surface-2);
    border-radius: 10px;
    border: 1px solid var(--border);
    font-size: 0.78rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    animation: stepSlideIn 0.3s ease-out both;
}

.pipeline-step:hover {
    border-color: var(--border-hover);
    background: var(--surface-3);
}

.pipeline-step.active {
    border-color: var(--accent);
    background: rgba(124, 58, 237, 0.08);
    box-shadow: 0 0 15px rgba(124, 58, 237, 0.1);
}

.pipeline-step.done {
    border-color: rgba(16, 185, 129, 0.3);
    background: rgba(16, 185, 129, 0.05);
}

@keyframes stepSlideIn {
    from { opacity: 0; transform: translateX(-10px); }
    to { opacity: 1; transform: translateX(0); }
}

.step-icon {
    width: 24px; height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    flex-shrink: 0;
    transition: all 0.3s;
}

.step-icon.pending {
    background: var(--surface-3);
    border: 2px solid var(--border);
    color: var(--text-dim);
}

.step-icon.active {
    background: rgba(124, 58, 237, 0.3);
    border: 2px solid var(--accent-glow);
    color: var(--accent-glow);
    animation: iconPulse 1.5s ease-in-out infinite;
}

.step-icon.done {
    background: rgba(16, 185, 129, 0.2);
    border: 2px solid var(--success);
    color: var(--success);
}

@keyframes iconPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(159, 103, 255, 0.4); }
    50% { box-shadow: 0 0 0 6px rgba(159, 103, 255, 0); }
}

.step-label {
    flex: 1;
    color: var(--text-muted);
    transition: color 0.3s;
}

.pipeline-step.active .step-label { color: var(--text); font-weight: 500; }
.pipeline-step.done .step-label   { color: var(--success); }

.step-time {
    font-size: 0.65rem;
    color: var(--text-dim);
    font-variant-numeric: tabular-nums;
}

/* ── Metrics Ribbon ── */
.metrics-ribbon {
    display: flex;
    gap: 1rem;
    margin: 1rem 0;
    flex-wrap: wrap;
}

.metric-card {
    flex: 1;
    min-width: 140px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: metricPop 0.4s ease-out both;
}

.metric-card:hover {
    transform: translateY(-3px);
    border-color: var(--accent);
    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.12);
}

@keyframes metricPop {
    from { opacity: 0; transform: scale(0.9); }
    to   { opacity: 1; transform: scale(1); }
}

.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-glow), var(--accent-2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.metric-label {
    font-size: 0.65rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 0.3rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: var(--surface) !important;
    border-radius: 12px;
    padding: 0.4rem;
    border: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: var(--text-muted) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.3s !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--text) !important;
    background: var(--surface-2) !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(6,182,212,0.1)) !important;
    color: var(--text) !important;
    border: 1px solid rgba(124,58,237,0.3) !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}

.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* ── Chat ── */
.chat-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.25rem;
    max-height: 480px;
    overflow-y: auto;
    margin-bottom: 1rem;
    scroll-behavior: smooth;
}

.chat-msg {
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    animation: msgFadeIn 0.4s ease-out both;
}

@keyframes msgFadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

.chat-label {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.chat-timestamp {
    font-size: 0.55rem;
    color: var(--text-dim);
    font-weight: 400;
    letter-spacing: 0.05em;
}

.chat-bubble {
    display: inline-block;
    padding: 0.7rem 1.1rem;
    border-radius: 14px;
    font-size: 0.85rem;
    line-height: 1.6;
    max-width: 88%;
    transition: all 0.2s;
}

.chat-bubble:hover {
    transform: scale(1.01);
}

.user-label  { color: var(--accent-glow); }
.bot-label   { color: var(--accent-2); }

.user-bubble {
    background: rgba(124,58,237,0.12);
    border: 1px solid rgba(124,58,237,0.25);
    align-self: flex-end;
    border-bottom-right-radius: 4px;
}

.bot-bubble {
    background: rgba(6,182,212,0.08);
    border: 1px solid rgba(6,182,212,0.2);
    align-self: flex-start;
    border-bottom-left-radius: 4px;
}

/* ── Typing Indicator ── */
.typing-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1rem;
    animation: msgFadeIn 0.3s ease-out;
}

.typing-dots {
    display: flex;
    gap: 4px;
}

.typing-dots span {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent-2);
    animation: typingBounce 1.4s ease-in-out infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
    30% { transform: translateY(-6px); opacity: 1; }
}

/* ── Suggestion Chips ── */
.chip-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.75rem;
}

.chip {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.45rem 0.9rem;
    border-radius: 20px;
    font-size: 0.75rem;
    background: var(--surface-2);
    border: 1px solid var(--border);
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.chip:hover {
    background: rgba(124,58,237,0.15);
    border-color: var(--accent);
    color: var(--text);
    transform: translateY(-1px);
}

/* ── Transcript Box ── */
.transcript-box {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.25rem;
    font-size: 0.82rem;
    line-height: 1.8;
    max-height: 400px;
    overflow-y: auto;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Session Card ── */
.session-card {
    padding: 0.65rem 0.85rem;
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 0.4rem;
    cursor: pointer;
    transition: all 0.25s;
    font-size: 0.75rem;
}

.session-card:hover {
    border-color: var(--accent);
    background: rgba(124,58,237,0.08);
}

.session-card.active {
    border-color: var(--accent);
    background: rgba(124,58,237,0.12);
    box-shadow: 0 0 10px rgba(124,58,237,0.1);
}

.session-title {
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.78rem;
    color: var(--text);
    margin-bottom: 0.2rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.session-meta {
    font-size: 0.62rem;
    color: var(--text-dim);
}

/* ── Empty State ── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 5rem 2rem;
    text-align: center;
}

.empty-icon {
    font-size: 4.5rem;
    margin-bottom: 1.5rem;
    animation: emptyFloat 3s ease-in-out infinite;
}

@keyframes emptyFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-12px); }
}

.empty-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.5rem;
}

.empty-desc {
    color: var(--text-muted);
    font-size: 0.85rem;
    max-width: 420px;
    line-height: 1.7;
}

/* ── Download Button ── */
.stDownloadButton > button {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    transition: all 0.3s !important;
}

.stDownloadButton > button:hover {
    border-color: var(--accent) !important;
    background: rgba(124,58,237,0.1) !important;
    transform: translateY(-1px) !important;
}

/* ── Misc ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

.stProgress > div > div > div { background: linear-gradient(90deg, var(--accent), var(--accent-2)) !important; }
.stSpinner > div { border-top-color: var(--accent) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }
label { color: var(--text-muted) !important; font-size: 0.8rem !important; }

/* scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── Toast ── */
.toast-success {
    position: fixed;
    top: 20px;
    right: 20px;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: var(--success);
    padding: 0.8rem 1.2rem;
    border-radius: 10px;
    font-size: 0.82rem;
    font-family: 'JetBrains Mono', monospace;
    z-index: 9999;
    animation: toastIn 0.4s ease-out, toastOut 0.4s ease-in 3s forwards;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    backdrop-filter: blur(10px);
}

@keyframes toastIn {
    from { opacity: 0; transform: translateX(30px); }
    to   { opacity: 1; transform: translateX(0); }
}

@keyframes toastOut {
    from { opacity: 1; transform: translateX(0); }
    to   { opacity: 0; transform: translateX(30px); }
}

/* ── Timer ── */
.timer-display {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--accent-glow);
    text-align: center;
    padding: 0.4rem 0;
    letter-spacing: 0.1em;
}
</style>
""", unsafe_allow_html=True)

# ─── Floating Orbs Background ──────────────────────────────────────────────────
st.markdown("""
<div class="orb-container">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
</div>
""", unsafe_allow_html=True)

# ─── Session State Init ─────────────────────────────────────────────────────────
defaults = {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
    "step_times": {},
    "total_time": 0,
    "sessions": [],          # list of past sessions
    "active_session": -1,    # index into sessions
    "show_toast": False,
}
for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
PIPELINE_STEPS = [
    ("audio",      "🔊", "Audio Processing"),
    ("transcript", "📝", "Transcription"),
    ("title",      "🏷️", "Title Generation"),
    ("summary",    "📋", "Summarisation"),
    ("extract",    "🔍", "Extraction"),
    ("rag",        "🧠", "RAG Engine"),
]

SUGGESTED_QUESTIONS = [
    "What were the main decisions made?",
    "Summarize the key takeaways",
    "Were there any disagreements?",
    "What action items were assigned?",
    "Who spoke the most?",
    "What topics need follow-up?",
]

def count_words(text: str) -> int:
    return len(text.split()) if text else 0

def count_action_items(text: str) -> int:
    if not text:
        return 0
    count = 0
    for line in text.strip().split("\n"):
        stripped = line.strip()
        if stripped and (stripped[0].isdigit() or stripped.startswith("-") or stripped.startswith("•")):
            count += 1
    return max(count, 1)

def render_pipeline_sidebar():
    """Render the animated pipeline progress in the sidebar."""
    steps = st.session_state.pipeline_steps
    times = st.session_state.step_times

    html = '<div class="pipeline-container">'
    for i, (key, icon, label) in enumerate(PIPELINE_STEPS):
        state = steps.get(key, "pending")
        css_class = state  # pending | active | done
        step_delay = f"animation-delay: {i * 0.08}s;"

        time_str = ""
        if key in times:
            t = times[key]
            time_str = f'<span class="step-time">{t:.1f}s</span>'

        icon_char = "⏳" if state == "pending" else ("⚡" if state == "active" else "✓")

        html += f'''
        <div class="pipeline-step {css_class}" style="{step_delay}">
            <div class="step-icon {state}">{icon_char}</div>
            <span class="step-label">{icon} {label}</span>
            {time_str}
        </div>'''
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def load_session(index: int):
    """Switch to a saved session."""
    if 0 <= index < len(st.session_state.sessions):
        session = st.session_state.sessions[index]
        st.session_state.result = session["result"]
        st.session_state.chat_history = session.get("chat_history", [])
        st.session_state.pipeline_done = True
        st.session_state.pipeline_steps = {k: "done" for k, _, _ in PIPELINE_STEPS}
        st.session_state.step_times = session.get("step_times", {})
        st.session_state.total_time = session.get("total_time", 0)
        st.session_state.active_session = index

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title" style="font-size:1.6rem">🎬 AI<br>Video</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Meeting Intelligence</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<span class="badge badge-purple">Input</span>', unsafe_allow_html=True)
    input_mode = st.radio(
        "Input Method",
        ["🔗 YouTube URL / Path", "📁 Upload File"],
        horizontal=True,
        label_visibility="collapsed",
    )

    source = ""
    uploaded_file = None

    if input_mode == "🔗 YouTube URL / Path":
        source = st.text_input(
            "YouTube URL or File Path",
            placeholder="https://youtube.com/watch?v=... or /path/to/file.mp4",
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload audio or video file",
            type=["mp4", "mp3", "wav", "m4a", "webm", "ogg", "flac", "mkv", "avi"],
            help="Drag and drop or click to browse",
        )
        if uploaded_file:
            st.markdown(
                f'<div class="status-bar" style="margin-top:0.3rem">' 
                f'<div class="status-dot dot-done"></div>'
                f'<span style="font-size:0.75rem">{uploaded_file.name} ({uploaded_file.size / 1024:.0f} KB)</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    language = st.selectbox("Language", ["english", "hinglish"], index=0)
    run_btn = st.button("⚡  Analyse", use_container_width=True)

    # ── Pipeline Status ──
    if st.session_state.pipeline_done or st.session_state.pipeline_steps:
        st.markdown("---")
        st.markdown('<span class="badge badge-green">Pipeline Status</span>', unsafe_allow_html=True)
        render_pipeline_sidebar()

        if st.session_state.total_time > 0:
            st.markdown(
                f'<div class="timer-display">⏱️ Total: {st.session_state.total_time:.1f}s</div>',
                unsafe_allow_html=True,
            )

    # ── Session History ──
    if st.session_state.sessions:
        st.markdown("---")
        st.markdown('<span class="badge badge-pink">Session History</span>', unsafe_allow_html=True)

        for i, session in enumerate(reversed(st.session_state.sessions)):
            real_idx = len(st.session_state.sessions) - 1 - i
            is_active = real_idx == st.session_state.active_session
            active_cls = "active" if is_active else ""
            title = session["result"].get("title", "Untitled")[:40]
            ts = session.get("timestamp", "")

            st.markdown(f'''
            <div class="session-card {active_cls}">
                <div class="session-title">{"▸ " if is_active else ""}{title}</div>
                <div class="session-meta">{ts}</div>
            </div>
            ''', unsafe_allow_html=True)

            if st.button(f"Load", key=f"load_{real_idx}", use_container_width=True):
                load_session(real_idx)
                st.rerun()

# ─── Main Area ──────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">AI Video Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Transcribe · Summarise · Chat with your meetings</div>', unsafe_allow_html=True)
st.markdown("---")

# ─── Run Pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    # Determine the source: uploaded file or text input
    effective_source = None

    if uploaded_file is not None:
        # Save uploaded file to disk so the pipeline can process it
        upload_dir = "downloades"
        os.makedirs(upload_dir, exist_ok=True)
        saved_path = os.path.join(upload_dir, uploaded_file.name)
        with open(saved_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        effective_source = saved_path
    elif source and source.strip():
        effective_source = source.strip()

    if not effective_source:
        st.error("⚠️ Please enter a YouTube URL, file path, or upload a file.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}
        st.session_state.step_times = {}
        st.session_state.total_time = 0
        st.session_state.show_toast = False

        progress_placeholder = st.empty()
        pipeline_start = time.time()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        def timed_step(key, fn, *args, **kwargs):
            """Run a pipeline step, time it, and update status."""
            update_step(key, "active")
            t0 = time.time()
            result = fn(*args, **kwargs)
            elapsed = time.time() - t0
            st.session_state.step_times[key] = elapsed
            update_step(key, "done")
            return result

        try:
            with progress_placeholder.container():
                st.info("⚙️ Pipeline running — see sidebar for live status…")

            chunks = timed_step("audio", process_input, effective_source)
            transcript = timed_step("transcript", transcribe_all, chunks, language)
            title = timed_step("title", generate_title, transcript)
            summary_text = timed_step("summary", summarize, transcript)

            # Extraction step — multiple calls
            update_step("extract", "active")
            t0 = time.time()
            action_items = extract_action_items(transcript)
            decisions    = extract_key_decisions(transcript)
            questions    = extract_questions(transcript)
            st.session_state.step_times["extract"] = time.time() - t0
            update_step("extract", "done")

            rag_chain = timed_step("rag", build_rag_chain, transcript)

            total_elapsed = time.time() - pipeline_start
            st.session_state.total_time = total_elapsed

            result = {
                "title": title,
                "transcript": transcript,
                "summary": summary_text,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
                "chunks_count": len(chunks),
            }

            st.session_state.result = result
            st.session_state.pipeline_done = True
            st.session_state.show_toast = True

            # Save to session history
            st.session_state.sessions.append({
                "result": result,
                "chat_history": [],
                "step_times": dict(st.session_state.step_times),
                "total_time": total_elapsed,
                "timestamp": datetime.datetime.now().strftime("%I:%M %p · %b %d"),
            })
            st.session_state.active_session = len(st.session_state.sessions) - 1

            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            for k in ["audio", "transcript", "title", "summary", "extract", "rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_placeholder.error(f"❌ Error: {e}")

# ─── Toast Notification ─────────────────────────────────────────────────────────
if st.session_state.show_toast:
    st.markdown(
        '<div class="toast-success">✅ Analysis complete! Results are ready.</div>',
        unsafe_allow_html=True,
    )
    st.session_state.show_toast = False

# ─── Results ────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # ── Title Banner ──
    st.markdown(f"""
    <div class="card" style="animation-delay: 0.1s;">
        <div class="card-title">📌 Session Title</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:700;color:var(--text)">
            {r['title']}
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Metrics Ribbon ──
    word_count = count_words(r.get("transcript", ""))
    action_count = count_action_items(r.get("action_items", ""))
    chunks = r.get("chunks_count", 0)
    proc_time = st.session_state.total_time

    st.markdown(f"""
    <div class="metrics-ribbon">
        <div class="metric-card" style="animation-delay: 0.15s;">
            <div class="metric-value">{proc_time:.1f}s</div>
            <div class="metric-label">⏱️ Processing Time</div>
        </div>
        <div class="metric-card" style="animation-delay: 0.25s;">
            <div class="metric-value">{word_count:,}</div>
            <div class="metric-label">📊 Word Count</div>
        </div>
        <div class="metric-card" style="animation-delay: 0.35s;">
            <div class="metric-value">{chunks}</div>
            <div class="metric-label">🧩 Audio Chunks</div>
        </div>
        <div class="metric-card" style="animation-delay: 0.45s;">
            <div class="metric-value">{action_count}</div>
            <div class="metric-label">🎯 Action Items</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabbed Dashboard ──
    tab_summary, tab_transcript, tab_insights, tab_chat = st.tabs([
        "📋 Summary", "📝 Transcript", "✅ Insights", "💬 Chat"
    ])

    # ─── TAB: Summary ────────────────────────────────────────────────────────
    with tab_summary:
        st.markdown(f"""
        <div class="card" style="animation-delay: 0.2s;">
            <div class="card-title">📋 Meeting Summary</div>
            <div class="card-content">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)

        st.download_button(
            label="📥 Download Summary",
            data=f"# {r['title']}\n\n{r['summary']}",
            file_name="meeting_summary.txt",
            mime="text/plain",
        )

    # ─── TAB: Transcript ─────────────────────────────────────────────────────
    with tab_transcript:
        st.markdown(f"""
        <div class="card" style="animation-delay: 0.2s;">
            <div class="card-title">📝 Full Transcript
                <span class="badge badge-cyan" style="margin-left:auto">{word_count:,} words</span>
            </div>
            <div class="transcript-box">{r['transcript']}</div>
        </div>""", unsafe_allow_html=True)

        st.download_button(
            label="📥 Download Transcript",
            data=r["transcript"],
            file_name="meeting_transcript.txt",
            mime="text/plain",
        )

    # ─── TAB: Insights ───────────────────────────────────────────────────────
    with tab_insights:
        c1, c2, c3 = st.columns(3, gap="medium")

        with c1:
            st.markdown(f"""
            <div class="card" style="animation-delay: 0.15s;">
                <div class="card-title">✅ Action Items</div>
                <div class="card-content">{r['action_items']}</div>
            </div>""", unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="card" style="animation-delay: 0.25s;">
                <div class="card-title">🔑 Key Decisions</div>
                <div class="card-content">{r['key_decisions']}</div>
            </div>""", unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="card" style="animation-delay: 0.35s;">
                <div class="card-title">❓ Open Questions</div>
                <div class="card-content">{r['open_questions']}</div>
            </div>""", unsafe_allow_html=True)

        # Combined download
        insights_text = (
            f"# Action Items\n{r['action_items']}\n\n"
            f"# Key Decisions\n{r['key_decisions']}\n\n"
            f"# Open Questions\n{r['open_questions']}"
        )
        st.download_button(
            label="📥 Download All Insights",
            data=insights_text,
            file_name="meeting_insights.txt",
            mime="text/plain",
        )

    # ─── TAB: Chat ───────────────────────────────────────────────────────────
    with tab_chat:
        st.markdown(
            '<div style="font-family:\'Syne\',sans-serif;font-size:1.15rem;font-weight:700;'
            'margin-bottom:0.8rem">💬 Chat with your Meeting</div>',
            unsafe_allow_html=True,
        )

        # Chat history display
        if st.session_state.chat_history:
            chat_html = '<div class="chat-container">'
            for idx, msg in enumerate(st.session_state.chat_history):
                delay = f"animation-delay: {min(idx * 0.05, 0.5)}s;"
                ts = msg.get("timestamp", "")
                if msg["role"] == "user":
                    chat_html += f"""
                    <div class="chat-msg" style="align-items:flex-end;{delay}">
                        <span class="chat-label user-label">You <span class="chat-timestamp">{ts}</span></span>
                        <div class="chat-bubble user-bubble">{msg['content']}</div>
                    </div>"""
                else:
                    chat_html += f"""
                    <div class="chat-msg" style="align-items:flex-start;{delay}">
                        <span class="chat-label bot-label">🤖 Assistant <span class="chat-timestamp">{ts}</span></span>
                        <div class="chat-bubble bot-bubble">{msg['content']}</div>
                    </div>"""
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)
        else:
            # Empty chat state with suggested questions
            st.markdown("""
            <div class="card" style="text-align:center;padding:2rem">
                <div style="font-size:2.5rem;margin-bottom:0.5rem">💬</div>
                <div style="color:var(--text-muted);font-size:0.85rem;margin-bottom:1rem">
                    Ask anything about your meeting transcript
                </div>
                <div style="color:var(--text-dim);font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem">
                    Try asking
                </div>
            </div>""", unsafe_allow_html=True)

        # Suggested question chips
        if not st.session_state.chat_history:
            chip_cols = st.columns(3)
            for i, q in enumerate(SUGGESTED_QUESTIONS):
                with chip_cols[i % 3]:
                    if st.button(f"💡 {q}", key=f"chip_{i}", use_container_width=True):
                        now = datetime.datetime.now().strftime("%I:%M %p")
                        st.session_state.chat_history.append(
                            {"role": "user", "content": q, "timestamp": now}
                        )
                        with st.spinner(""):
                            # Show typing indicator feel
                            answer = ask_question(r["rag_chain"], q)
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": answer, "timestamp": now}
                        )
                        # Sync chat to session history
                        if st.session_state.active_session >= 0:
                            st.session_state.sessions[st.session_state.active_session]["chat_history"] = list(st.session_state.chat_history)
                        st.rerun()

        # Chat input row
        chat_col1, chat_col2 = st.columns([5, 1], gap="small")
        with chat_col1:
            user_input = st.text_input(
                "Your question",
                placeholder="Ask something about the meeting...",
                label_visibility="collapsed",
            )
        with chat_col2:
            send_btn = st.button("Send →", use_container_width=True, key="send_chat")

        if send_btn and user_input.strip():
            now = datetime.datetime.now().strftime("%I:%M %p")
            st.session_state.chat_history.append(
                {"role": "user", "content": user_input.strip(), "timestamp": now}
            )
            with st.spinner(""):
                answer = ask_question(r["rag_chain"], user_input.strip())
            st.session_state.chat_history.append(
                {"role": "assistant", "content": answer, "timestamp": now}
            )
            # Sync chat to session history
            if st.session_state.active_session >= 0:
                st.session_state.sessions[st.session_state.active_session]["chat_history"] = list(st.session_state.chat_history)
            st.rerun()

        # Clear chat button
        if st.session_state.chat_history:
            if st.button("🗑️ Clear Chat", type="secondary"):
                st.session_state.chat_history = []
                if st.session_state.active_session >= 0:
                    st.session_state.sessions[st.session_state.active_session]["chat_history"] = []
                st.rerun()

else:
    # ── Empty State ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🎬</div>
        <div class="empty-title">Ready to Analyse</div>
        <div class="empty-desc">
            Paste a YouTube URL or local file path in the sidebar,
            choose your language, and hit <strong>Analyse</strong> to get started.
        </div>
        <div style="margin-top:2rem;display:flex;gap:1rem;flex-wrap:wrap;justify-content:center">
            <span class="badge badge-purple">Transcription</span>
            <span class="badge badge-cyan">Summarisation</span>
            <span class="badge badge-green">RAG Chat</span>
            <span class="badge badge-pink">Export</span>
        </div>
    </div>""", unsafe_allow_html=True)