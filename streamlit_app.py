import streamlit as st

from chatbot.memory import Memory
from chatbot.prompt_loader import load_prompt

from services.question_processor import process_question

from ui.sidebar import render_sidebar
from ui.chat import render_chat


st.title("GurAI")

st.write("Agente de IA especializado em operações de eletropostos.")

conta_pergunta = []

if "memory" not in st.session_state:

    system_prompt = load_prompt()

    st.session_state.memory = Memory(

        system_prompt

    )

# ------------------------------------------------------------------ #

#                       Histórico do chat.                           #

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


for message in st.session_state.chat_history:

    with st.chat_message(message["role"]):
        st.write(message["content"])

# ------------------------------------------------------------------ #

render.sidebar()

render_chat()


question = st.chat_input(
    "Digite sua pergunta",
    
)


# ------------------------------------------------------------------ #

if question:


    answer = process_question(
        question,
        st.session_state.memory
    )
    

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": question
        }
    )

    st.session_state.chat_history.append(
        {
            "role": "asistant",
            "content": answer
        }
    )

    st.rerun()

# ------------------------------------------------------------------ #



        







