import plotly.express as px
import streamlit as st


EMOTION_ORDER = ["anxious", "angry", "sad", "tired", "neutral"]


def _safe_score(value) -> float:
    try:
        return round(float(value), 3)
    except (TypeError, ValueError):
        return 0.0


def render_emotion_chart(emotion: dict | None):
    if not emotion:
        st.info("Emotion insights will appear after a chat run.")
        return

    scores = emotion.get("scores") or {}
    if not isinstance(scores, dict) or not scores:
        st.warning("No emotion scores available for charting.")
        return

    labels = EMOTION_ORDER if set(EMOTION_ORDER) >= set(scores.keys()) else list(scores.keys())
    values = [_safe_score(scores.get(label, 0.0)) for label in labels]

    title = f"Emotion: {emotion.get('label', 'unknown').title()} (intensity {emotion.get('intensity', '?')})"
    fig = px.line(
        x=labels,
        y=values,
        markers=True,
        labels={"x": "emotion", "y": "score"},
        title=title,
        range_y=[0, 1],
        template="plotly_dark",
        color_discrete_sequence=["#22d3ee"],
    )
    fig.update_layout(
        paper_bgcolor="#0b1220",
        plot_bgcolor="#0b1220",
        font_color="#e5e7eb",
        margin=dict(l=20, r=20, t=60, b=20),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
