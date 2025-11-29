import streamlit as st


def render_chat_panel(default_text: str, key: str = "user_text") -> str:
    st.subheader("Mindful Chat")
    st.caption("Share how you feel. The more specific the better—include situations, sensations, or thoughts.")
    return st.text_area(
        "What would you like to share?",
        value=default_text,
        height=180,
        key=key,
        help="This text will be sent to the orchestrator.",
    )
