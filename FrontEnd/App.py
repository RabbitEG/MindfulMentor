import streamlit as st

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
        line-height: 1.6;
    }
    .stApp {
        background: radial-gradient(circle at 20% 25%, #0b1220 0%, #0d1424 45%, #0f172a 80%);
        color: #e5e7eb;
    }
    .block-container {
        max-width: 780px;
        padding: 24px 20px 60px 20px;
        margin: 0 auto;
    }
    h1, h2, h3, .stRadio label, .stButton button {
        color: #e5e7eb !important;
    }
    .page-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    }
    .hero {
        padding: 0.75rem 1rem;
        border-radius: 14px;
        background: linear-gradient(135deg, #111827, #0f172a 70%);
        color: #e5e7eb;
        border: 1px solid #1e293b;
        box-shadow: 0 12px 30px rgba(0,0,0,0.28);
        margin-bottom: 1rem;
    }
    .stForm {
        background: rgba(17, 24, 39, 0.8);
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 1rem 1.25rem 1.1rem 1.25rem;
        box-shadow: 0 16px 40px rgba(0,0,0,0.25);
    }
    .cardish {
        background: rgba(17, 24, 39, 0.8);
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 1rem 1.25rem;
        box-shadow: 0 16px 40px rgba(0,0,0,0.25);
    }
    .stTextArea textarea {
        background-color: #0b1220 !important;
        color: #e5e7eb !important;
        border: 1px solid #1f2937;
        border-radius: 12px;
        line-height: 1.6 !important;
    }
    .stRadio [role="radiogroup"] {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .stRadio [role="radiogroup"] label {
        background: #0f172a;
        padding: 0.45rem 0.9rem;
        border-radius: 999px;
        border: 1px solid #1f2937;
        color: #e5e7eb;
        font-weight: 600;
        cursor: pointer;
    }
    .stRadio [role="radiogroup"] label:hover {
        border-color: #38bdf8;
    }
    .stRadio [role="radiogroup"] label:has(input:checked) {
        background: #1e293b;
        border-color: #38bdf8;
        box-shadow: 0 0 0 1px #0ea5e9 inset;
        color: #f9fafb;
    }
    .stButton button {
        background: linear-gradient(135deg, #22d3ee, #2563eb);
        border: none;
        color: #0b1220 !important;
        font-weight: 700;
        height: 46px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(34,211,238,0.25);
    }
    .stButton button:hover {
        filter: brightness(1.05);
    }
    .stButton button:focus-visible {
        outline: 2px solid #38bdf8;
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
    .section-gap {
        height: 18px;
    }
    .diagram {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
        margin-top: 8px;
    }
    .diagram .node {
        padding: 6px 10px;
        border-radius: 10px;
        border: 1px solid #1f2937;
        background: #0f172a;
        color: #e5e7eb;
        font-size: 0.9rem;
        white-space: nowrap;
    }
    .diagram .arrow {
        color: #38bdf8;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state["history"] = []
if "last_response" not in st.session_state:
    st.session_state["last_response"] = None
if "flow" not in st.session_state:
    st.session_state["flow"] = "chat"
if "dev_mode" not in st.session_state:
    st.session_state["dev_mode"] = False

header_left, header_right = st.columns([6, 2])
with header_left:
    st.title("MindfulMentor")
    st.caption("Emotion-aware responses without the rough edges.")
with header_right:
    st.checkbox("Developer mode", key="dev_mode")

st.markdown(
    '<div class="hero">Send a feeling and get a safe, empathic reply. Choose chat, breathing, or thought clarify.</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

default_text = (
    "I keep staring at my screen because the deadlines are piling up. "
    "My shoulders are tense and I haven't slept well this week. "
    "I worry my team will think I'm dropping the ball, even though I'm trying. "
    "Can you help me figure out where to start?"
)

with st.form("chat_form"):
    st.subheader("Mindful Chat")
    st.caption("Share what's on your mind. The more specific, the better.")
    user_text = st.text_area(
        "What would you like to share?",
        value=default_text,
        height=190,
        placeholder="I keep staring at my screen because the deadlines are piling up...",
        help="English only.",
    )
    st.markdown("#### Pick a flow")
    with st.container():
        flow = st.radio(
            "",
            options=["chat", "breathing", "thought-clarify"],
            index=["chat", "breathing", "thought-clarify"].index(st.session_state.get("flow", "chat")),
            format_func=lambda x: {"chat": "Chat", "breathing": "Breathing", "thought-clarify": "Thought Clarify"}[x],
            horizontal=True,
            key="flow_radio",
            label_visibility="collapsed",
        )
        st.session_state["flow"] = flow

    col_gap, col_submit = st.columns([3, 1])
    with col_submit:
        submitted = st.form_submit_button("Send", use_container_width=True)
    with col_gap:
        st.caption(" ")

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

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

st.subheader("Introduction")
st.caption("MindfulMentor turns feelings into prompts and routes them through an LLM for safe, emotion-aware replies.")
with st.expander("Show details", expanded=False):
    st.markdown(
        """
        **Services**
        - EmotionService → detect dominant emotion and intensity
        - PromptEngine → choose the right prompt template
        - LlmGateway → call the model with fallback
        - Orchestrator → stitch safety, prompt, and generation
        - FrontEnd → capture input, visualize results

        **Flow**
        - classify the dominant emotion
        - generate an appropriate prompt
        - call the model through the gateway
        - render the reply with emotion scores
        """
    )
    st.markdown(
        """
        <div class="diagram">
          <div class="node">EmotionService</div>
          <div class="arrow">→</div>
          <div class="node">PromptEngine</div>
          <div class="arrow">→</div>
          <div class="node">LlmGateway</div>
          <div class="arrow">→</div>
          <div class="node">Orchestrator</div>
          <div class="arrow">→</div>
          <div class="node">FrontEnd</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

col_main, col_side = st.columns([1.2, 0.9])
with col_main:
    render_response_panel(response, dev_mode=st.session_state["dev_mode"])

with col_side:
    render_emotion_chart(st.session_state["history"], dev_mode=st.session_state["dev_mode"])
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
render_history(st.session_state["history"], dev_mode=st.session_state["dev_mode"])

if st.session_state["dev_mode"]:
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    st.subheader("Developer tools")
    if response:
        st.caption(f"Last trace id: {response.get('trace_id') or '—'}")
        with st.expander("Last response JSON", expanded=False):
            st.json(response)
    else:
        st.caption("No responses yet.")
