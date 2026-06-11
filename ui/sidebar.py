
import streamlit as st

def render_sidebar():
    with st.sidebar:

        st.title("Perguntas realizadas")

        for message in st.session_state.chat_history[-10:]:
            if message["role"] == "user":

                st.write(
                    message["content"]
                )

