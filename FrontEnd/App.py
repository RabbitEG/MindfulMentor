import streamlit as st

from Components.ChatPanel import render_chat_panel
from Components.EmotionChart import render_emotion_chart
from Components.ExerciseCards import render_exercise_cards
from Components.History import render_history
from Components.ResponsePanel import render_response_panel
from Utils import call_orchestrator

st.set_page_config(page_title="MindfulMentor", page_icon="🧘", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Space Grotesk', sans-serif;
        color: #e5e7eb;
    }
    .stApp {
        background: radial-gradient(circle at 20% 25%, #0b1220 0%, #0d1424 45%, #0f172a 80%);
        color: #e5e7eb;
    }
    .hero {
        padding: 1rem 1.5rem;
        border-radius: 14px;
        background: linear-gradient(135deg, #111827, #0f172a 70%);
        color: #e5e7eb;
        border: 1px solid #1e293b;
        box-shadow: 0 12px 30px rgba(0,0,0,0.28);
        margin-bottom: 1rem;
    }
    h1, h2, h3, .stRadio label, .stButton button {
        color: #e5e7eb !important;
    }
    .stTextArea textarea {
        background-color: #0b1220 !important;
        color: #e5e7eb !important;
        border: 1px solid #1f2937;
        border-radius: 10px;
    }
    .stRadio [role="radiogroup"] > label {
        background: #111827;
        padding: 0.35rem 0.7rem;
        border-radius: 10px;
        border: 1px solid #1f2937;
        color: #e5e7eb;
    }
    .stButton button {
        background: linear-gradient(135deg, #22d3ee, #2563eb);
        border: none;
        color: #0b1220 !important;
        font-weight: 700;
    }
    .stAlert {
        background: rgba(34, 51, 84, 0.6) !important;
    }
    .info-card {
        padding: 0.85rem 1rem;
        border-radius: 12px;
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid #1f2937;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state["history"] = []
if "last_response" not in st.session_state:
    st.session_state["last_response"] = None

st.title("MindfulMentor")
st.caption("Emotion awareness + safe responses")
st.markdown(
    '<div class="hero">Send a feeling, get an empathic reply, and keep the trace id for debugging. Choose between chat, breathing, or thought clarify flows.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="info-card">
    <strong>Introduction</strong><br/>
    MindfulMentor is a small multi-service demo that turns free-text feelings into structured prompts, routes them through an LLM, and returns a safe, emotion-aware response.<br/><br/>
    It connects five independent services—EmotionService, PromptEngine, LlmGateway, Orchestrator, and this FrontEnd—to show how a minimal emotion-aware flow can be assembled end-to-end.<br/><br/>
    Type anything you feel, pick a flow (chat / breathing / thought-clarify), and the system will:<br/>
    · classify the dominant emotion,<br/>
    · generate an appropriate prompt,<br/>
    · call the model through the gateway,<br/>
    · and render the model’s reply together with the trace id for debugging.<br/><br/>
    This demo focuses on architecture clarity rather than content. See the README for diagrams and flow notes.
    </div>
    """,
    unsafe_allow_html=True,
)

default_text = (
    "I keep staring at my screen because the deadlines are piling up. "
    "My shoulders are tense and I haven't slept well this week. "
    "I worry my team will think I'm dropping the ball, even though I'm trying. "
    "Can you help me figure out where to start?"
)
with st.form("chat_form"):
    user_text = render_chat_panel(default_text)
    col_flow, col_submit = st.columns([3, 1])
    with col_flow:
        flow = st.radio(
            "Pick a flow",
            options=["chat", "breathing", "thought-clarify"],
            format_func=lambda x: {"chat": "Chat", "breathing": "Breathing", "thought-clarify": "Thought Clarify"}[x],
            horizontal=True,
        )
    with col_submit:
        submitted = st.form_submit_button("Send", use_container_width=True)

response = st.session_state.get("last_response")
if submitted:
    endpoint_map = {
        "chat": "/chat",
        "breathing": "/breathing",
        "thought-clarify": "/thought-clarify",
    }
    endpoint = endpoint_map[flow]
    with st.spinner(f"Calling {flow} flow..."):
        response = call_orchestrator(endpoint, {"text": user_text})
    st.session_state["last_response"] = response
    st.session_state["history"].insert(0, {"flow": flow, "input": user_text, "response": response})
    st.session_state["history"] = st.session_state["history"][:8]

col_main, col_side = st.columns([2.2, 1])
with col_main:
    render_response_panel(response)

with col_side:
    render_emotion_chart(st.session_state["history"])
    suggested = []
    meta = response.get("meta", {}) if response else {}
    if meta:
        raw_suggest = meta.get("suggestedExercise") or meta.get("suggestedExercises")
        if isinstance(raw_suggest, str):
            suggested = [s.strip() for s in raw_suggest.split(",") if s.strip()]
        elif isinstance(raw_suggest, list):
            suggested = raw_suggest
    render_exercise_cards(suggested)

st.divider()
render_history(st.session_state["history"])
