import streamlit as st


def render_chat_panel(default_text: str) -> str:
    st.subheader("Mindful Chat")
    return st.text_area("What would you like to share?", value=default_text, height=150)
