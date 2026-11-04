import os
from pathlib import Path

import streamlit as st
from google import genai

# ──────────────────────────────────────────────────────────────
# Config (no secrets in code)
# ──────────────────────────────────────────────────────────────
# Local: set env var GEMINI_API_KEY, or create .streamlit/secrets.toml
# Streamlit Cloud: App settings -> Secrets -> GEMINI_API_KEY = "your key"
def get_secret(name, default=None):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.environ.get(name, default)


API_KEY = get_secret("GEMINI_API_KEY")
MODEL = get_secret("GEMINI_MODEL", "gemini-flash-latest")  # alias to newest Flash model

# KB file is looked up next to app.py, so it works locally and on Streamlit Cloud
KB_PATH = Path(__file__).parent / "python_chatbot.txt"

try:
    kb = KB_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    kb = None

PROMPT = f"""
You are a Python chatbot. Your job is to answer Python questions using ONLY the knowledge base below.
Understand the user's natural-language question and answer it correctly and clearly.
If you don't understand the question, say "I can't understand the question."
If the question is not covered by the knowledge base, say "I don't have that information."
Never answer from outside the knowledge base.

KNOWLEDGE BASE:
{kb}
"""


@st.cache_resource
def get_client(key):
    return genai.Client(api_key=key)


def new_chat():
    return get_client(API_KEY).chats.create(
        model=MODEL,
        config={"system_instruction": PROMPT},
    )


# ──────────────────────────────────────────────────────────────
# Page setup
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Python Chatbot",
    page_icon="🐍",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --ink: #1b2433;
        --muted: #5d6b7e;
        --paper: #f5f7fa;
        --card: #ffffff;
        --line: #dde3ec;
        --py-blue: #2b5b84;
        --py-blue-deep: #1b3a57;
        --py-yellow: #ffd43b;
        --user-tint: #e6eef7;
    }

    html, body, [class*="css"], .stApp, .stMarkdown, p, li, label, input, textarea, button {
        font-family: 'Figtree', system-ui, sans-serif !important;
    }
    code, pre, pre * { font-family: 'JetBrains Mono', ui-monospace, monospace !important; }

    .stApp { background: var(--paper); color: var(--ink); }
    .stApp p, .stApp li, .stApp span, .stApp h1, .stApp h2, .stApp h3 { color: var(--ink); }

    /* Hide default Streamlit chrome */
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .block-container { padding-top: 2rem; padding-bottom: 6rem; max-width: 760px; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background: var(--py-blue-deep); }
    section[data-testid="stSidebar"] * { color: #e8eef5 !important; }
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: var(--py-yellow);
        color: var(--py-blue-deep) !important;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1rem;
    }
    section[data-testid="stSidebar"] .stButton > button:hover { background: #ffe07a; }
    section[data-testid="stSidebar"] .stButton > button p { color: var(--py-blue-deep) !important; font-weight: 600; }
    .side-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 0.2rem; }
    .side-sub { font-size: 0.9rem; opacity: 0.8; line-height: 1.45; margin-bottom: 1.2rem; }
    .side-stat { font-size: 0.85rem; opacity: 0.75; margin-top: 1rem; }

    /* Header */
    .hero { display: flex; align-items: center; gap: 0.9rem; margin-bottom: 0.4rem; }
    .hero-badge {
        width: 48px; height: 48px; border-radius: 14px;
        background: var(--py-blue);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem;
        box-shadow: inset 0 -4px 0 var(--py-yellow);
    }
    .hero h1 { font-size: 1.9rem; font-weight: 700; margin: 0; letter-spacing: -0.02em; }
    .hero-sub { color: var(--muted); font-size: 1rem; margin: 0 0 1.4rem 0; }

    /* Empty state */
    .empty-title { font-size: 1.1rem; font-weight: 600; margin: 1.6rem 0 0.2rem 0; }
    .empty-sub { color: var(--muted); font-size: 0.95rem; margin-bottom: 0.9rem; }

    /* Suggestion buttons (main area) */
    .main .stButton > button, div[data-testid="stMain"] .stButton > button {
        background: var(--card);
        color: var(--ink);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 0.7rem 1rem;
        text-align: left;
        font-weight: 500;
        transition: border-color .15s, background .15s;
    }
    div[data-testid="stMain"] .stButton > button:hover {
        border-color: var(--py-blue);
        background: #f0f5fa;
    }
    div[data-testid="stMain"] .stButton > button p { color: var(--ink); }

    /* Chat messages */
    div[data-testid="stChatMessage"] {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.8rem;
    }
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background: var(--user-tint);
        border-color: #cfdcec;
    }
    div[data-testid="stChatMessage"] pre {
        background: #14233a; border-radius: 10px;
    }
    div[data-testid="stChatMessage"] pre code { color: #e8eef5; }
    div[data-testid="stChatMessage"] :not(pre) > code {
        background: #eef2f7; color: var(--py-blue-deep); padding: 0.1rem 0.35rem; border-radius: 6px;
    }

    /* Chat input */
    div[data-testid="stChatInput"] { border-radius: 14px; border: 1px solid var(--line); background: var(--card); }
    div[data-testid="stChatInput"]:focus-within { border-color: var(--py-blue); box-shadow: 0 0 0 3px rgba(43,91,132,.15); }
    div[data-testid="stChatInput"] textarea { color: var(--ink); }
    div[data-testid="stChatInput"] button { background: var(--py-blue); color: #fff; border-radius: 10px; }

    @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────────────────────
if not API_KEY:
    st.error(
        "No API key found. Add `GEMINI_API_KEY` in Streamlit Cloud -> App settings -> Secrets "
        "(or in `.streamlit/secrets.toml` locally)."
    )
    st.stop()

if kb is None:
    st.error(
        f"Couldn't find the knowledge base file **{KB_PATH.name}**. "
        "Place it in the same folder as app.py."
    )
    st.stop()

if "chat" not in st.session_state:
    st.session_state.chat = new_chat()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending" not in st.session_state:
    st.session_state.pending = None

# ──────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="side-title">🐍 Python Chatbot</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-sub">Answers come only from the knowledge base. '
        "If a topic isn't covered, the bot will tell you.</div>",
        unsafe_allow_html=True,
    )
    if st.button("New chat", use_container_width=True):
        st.session_state.chat = new_chat()
        st.session_state.messages = []
        st.session_state.pending = None
        st.rerun()
    st.markdown(
        f'<div class="side-stat">{len(st.session_state.messages)} messages in this chat</div>',
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">🐍</div>
        <h1>Python Chatbot</h1>
    </div>
    <p class="hero-sub">Ask a Python question in plain English.</p>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────
# Empty state with starter questions
# ──────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown('<div class="empty-title">Start with a question</div>', unsafe_allow_html=True)
    st.markdown('<div class="empty-sub">Pick one below or type your own.</div>', unsafe_allow_html=True)

    suggestions = [
        "What is Python?",
        "What is a list in Python?",
        "How do I write a function?",
        "What is a dictionary?",
    ]
    cols = st.columns(2)
    for i, s in enumerate(suggestions):
        if cols[i % 2].button(s, key=f"sugg_{i}", use_container_width=True):
            st.session_state.pending = s
            st.rerun()

# ──────────────────────────────────────────────────────────────
# Chat history
# ──────────────────────────────────────────────────────────────
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🐍" if m["role"] == "assistant" else "🧑‍💻"):
        st.markdown(m["content"])

# ──────────────────────────────────────────────────────────────
# Input handling
# ──────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask a Python question...")
if not user_input and st.session_state.pending:
    user_input = st.session_state.pending
    st.session_state.pending = None

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🐍"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.chat.send_message(user_input)
                answer = response.text
            except Exception as e:
                answer = (
                    "Something went wrong while getting an answer. "
                    "Check your API key and model name, then try again."
                )
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
