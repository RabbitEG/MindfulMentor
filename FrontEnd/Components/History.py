import streamlit as st


def render_history(history: list[dict]):
    st.subheader("Recent Runs")
    if not history:
        st.caption("Your last few calls will appear here for quick inspection.")
        return

    for item in history[:5]:
        response = item.get("response", {})
        title = f"{item.get('flow', 'unknown')} · {response.get('trace_id', 'no-trace')}"
        with st.expander(title):
            st.markdown(f"**Input**: {item.get('input', '')}")
            st.markdown(f"**Message**: {response.get('message', '')}")
            emotion = response.get("emotion")
            if emotion:
                st.caption(
                    f"Emotion → {emotion.get('label', '')} / {emotion.get('intensity', '')} "
                    f"(score: {emotion.get('score', '0')})"
                )
