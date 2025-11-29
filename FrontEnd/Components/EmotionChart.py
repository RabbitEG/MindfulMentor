import plotly.express as px
import streamlit as st


def _safe_score(value) -> float:
    try:
        return round(float(value), 3)
    except (TypeError, ValueError):
        return 0.0


def render_emotion_chart(emotion: dict | None):
    if not emotion:
        st.info("Emotion insights will appear after a chat run.")
        return

    label = emotion.get("label", "unknown").title()
    score = _safe_score(emotion.get("score", 0.0))
    intensity = emotion.get("intensity", "low")
    fig = px.bar(
        x=["score"],
        y=[score],
        labels={"x": "metric", "y": "value"},
        title=f"Emotion: {label} ({intensity})",
        range_y=[0, 1],
        color_discrete_sequence=["#22d3ee"],
        template="plotly_dark",
    )
    fig.update_layout(
        paper_bgcolor="#0b1220",
        plot_bgcolor="#0b1220",
        font_color="#e5e7eb",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)
