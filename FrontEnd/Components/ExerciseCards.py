import streamlit as st


def render_exercise_cards():
    st.subheader("Recommended Practices")
    cols = st.columns(3)
    exercises = [
        ("Box Breathing", "Inhale 4s, hold 4s, exhale 4s, hold 4s."),
        ("Thought Labeling", "Name the feeling and its intensity without judgment."),
        ("Micro-action", "Pick one tiny step you can do in 2 minutes."),
    ]
    for col, (title, desc) in zip(cols, exercises):
        with col:
            st.write(f"**{title}**")
            st.write(desc)
