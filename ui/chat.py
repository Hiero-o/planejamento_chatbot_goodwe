import streamlit as st

def render_chat():
    for message in st.session_state.chat_history:
        with st.chat_message(
            message["role"]
        ):
            
            st.write(
                message["content"]
    
            )