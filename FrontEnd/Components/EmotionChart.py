import plotly.express as px
import streamlit as st


def render_emotion_chart(emotion: dict | None):
    if not emotion:
        return
    label = emotion.get("label", "unknown")
    score = emotion.get("score", 0.0)
    intensity = emotion.get("intensity", "low")
    fig = px.bar(
        x=["score"],
        y=[score],
        labels={"x": "metric", "y": "value"},
        title=f"Emotion: {label} ({intensity})",
        range_y=[0, 1],
    )
    st.plotly_chart(fig, use_container_width=True)
