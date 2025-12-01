import plotly.express as px
import streamlit as st


EMOTION_ORDER = ["anxious", "angry", "sad", "tired", "neutral"]


def _safe_score(value) -> float:
    try:
        return round(float(value), 3)
    except (TypeError, ValueError):
        return 0.0


def render_emotion_chart(history: list[dict], dev_mode: bool = False):
    st.subheader("Emotion Heatmap")

    if not history:
        st.info("Emotion insights will appear after you run a flow.")
        return

    rows: list[list[float]] = []
    y_labels: list[str] = []

    for idx, item in enumerate(history):
        response = item.get("response", {}) or {}
        emotion = response.get("emotion") or {}
        scores = emotion.get("scores") if isinstance(emotion, dict) else None
        if not isinstance(scores, dict) or not scores:
            continue

        row = [_safe_score(scores.get(label, 0.0)) for label in EMOTION_ORDER]
        rows.append(row)

        flow = item.get("flow", "unknown")
        label_parts = [f"{idx + 1}", flow]
        if dev_mode:
            trace = response.get("trace_id") or response.get("traceId") or (response.get("meta", {}) or {}).get("traceId")
            if trace:
                label_parts.append(trace[-6:] if isinstance(trace, str) and len(trace) >= 6 else str(trace))
        y_labels.append(" · ".join(label_parts))

    if not rows:
        st.info("No emotion scores available yet.")
        return

    fig = px.imshow(
        rows,
        x=EMOTION_ORDER,
        y=y_labels,
        color_continuous_scale="Blues",
        zmin=0,
        zmax=1,
        labels={"x": "emotion", "y": "run", "color": "score"},
        aspect="auto",
        origin="upper",
    )
    fig.update_layout(
        title="History × Emotion scores",
        paper_bgcolor="#0b1220",
        plot_bgcolor="#0b1220",
        font_color="#e5e7eb",
        margin=dict(l=20, r=20, t=60, b=20),
        coloraxis_showscale=True,
    )
    fig.update_xaxes(side="top")
    st.plotly_chart(fig, use_container_width=True)
