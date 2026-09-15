import streamlit as st

from services.question_processor import process_question

from ui.sidebar import render_sidebar
from ui.chat import render_chat


st.title("GurAI")

st.write("Agente de IA especializado em operações de eletropostos.")

conta_pergunta = []

if "session_id" not in st.session_state:
       st.session_state.session_id = "streamlit_session"

# ------------------------------------------------------------------ #

#                       Histórico do chat.                           #

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    

# ------------------------------------------------------------------ #

#                Guarda página - ui/sidebar.py                       #

if "sidebar_page" not in st.session_state:
            st.session_state.sidebar_page = "Monitoramento"

# ------------------------------------------------------------------ #


render_sidebar()

render_chat()


question = st.chat_input(
    "Digite sua pergunta",
    
)


# ------------------------------------------------------------------ #

if question:


    answer = process_question(
        question,
        st.session_state.session_id
    )
    

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": question
        }
    )

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    st.rerun()

# ------------------------------------------------------------------ #
