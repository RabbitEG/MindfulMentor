import streamlit as st


def render_response_panel(response: dict | None):
    st.subheader("Orchestrator Reply")
    if response is None:
        st.info("Ready when you are. Send a prompt to see the bot's response.")
        return

    error = response.get("error")
    if error:
        st.error(f"{error.get('code', 'error')}: {error.get('detail', '')}")
    else:
        st.success(response.get("message", ""))

    meta = response.get("meta") or {}
    trace_id = response.get("trace_id")
    cols = st.columns(2)
    with cols[0]:
        st.caption(f"trace_id: {trace_id or '—'}")
    with cols[1]:
        endpoint = meta.get("endpoint")
        if endpoint:
            st.caption(f"endpoint: {endpoint}")

    if meta:
        with st.expander("Meta (debug)", expanded=False):
            st.json(meta)
