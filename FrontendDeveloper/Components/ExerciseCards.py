import streamlit as st


def render_exercise_cards(suggested: list[str] | None = None):
    st.subheader("Recommended Practices")
    cols = st.columns(3)
    base = [
        ("Box Breathing", "Inhale 4s, hold 4s, exhale 4s, hold 4s."),
        ("Thought Labeling", "Name the feeling and its intensity without judgment."),
        ("Micro-action", "Pick one tiny step you can do in 2 minutes."),
    ]
    dynamic = []
    if suggested:
        for item in suggested:
            dynamic.append((item, "From orchestrator suggestion"))

    exercises = (dynamic + base)[:3]
    for col, (title, desc) in zip(cols, exercises):
        with col:
            st.write(f"**{title}**")
            st.write(desc)
