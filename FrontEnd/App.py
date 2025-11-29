import streamlit as st

from Components.ChatPanel import render_chat_panel
from Components.EmotionChart import render_emotion_chart
from Components.ExerciseCards import render_exercise_cards
from Utils import call_orchestrator

st.set_page_config(page_title="MindfulMentor", page_icon="🧘", layout="wide")
st.title("MindfulMentor")
st.caption("Emotion awareness + safe responses")

default_text = "I feel a bit overwhelmed by deadlines."
user_text = render_chat_panel(default_text)

col_left, col_right = st.columns([2, 1])

with col_left:
    if st.button("Send Chat"):
        result = call_orchestrator("/chat", {"text": user_text})
        st.success(result.get("message"))
        render_emotion_chart(result.get("emotion"))
    if st.button("Breathing Guide"):
        result = call_orchestrator("/breathing", {"text": user_text})
        st.info(result.get("message"))
    if st.button("Thought Clarify"):
        result = call_orchestrator("/thought-clarify", {"text": user_text})
        st.warning(result.get("message"))

with col_right:
    render_exercise_cards()
