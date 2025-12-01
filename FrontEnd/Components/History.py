import streamlit as st


def render_history(history: list[dict], dev_mode: bool = False):
    st.subheader("Recent Runs")
    if not history:
        st.caption("Your last few calls will appear here.")
        return

    for idx, item in enumerate(history[:5]):
        response = item.get("response", {})
        flow = item.get("flow", "unknown")
        trace = response.get("trace_id") or response.get("traceId") or (response.get("meta", {}) or {}).get("traceId")
        title = f"#{idx + 1} · {flow.title()}"
        if dev_mode and trace:
            title = f"{title} · {trace}"

        with st.expander(title):
            st.markdown(f"**Input**: {item.get('input', '')}")
            st.markdown(f"**Message**: {response.get('message', '')}")
            emotion = response.get("emotion")
            if emotion:
                st.caption(
                    f"Emotion → {emotion.get('label', '')} / {emotion.get('intensity', '')} "
                    f"(score: {emotion.get('score', '0')})"
                )
            if dev_mode and response.get("meta"):
                st.json(response.get("meta"))
