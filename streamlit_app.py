import streamlit as st
from chatbot.llm import ask_model
from chatbot.memory import Memory
from chatbot.prompt_loader import load_prompt
from services.monitoramento import *

st.title("GurAI")

st.write("Agente de IA especializado em operações de eletropostos.")


if "memory" not in st.session_state:

    system_prompt = load_prompt()

    st.session_state.memory = Memory(

        system_prompt

    )

question = st.chat_input(
    "Digite sua pergunta"
)

# ------------------------------------------------------------------ #

if question:

    st.session_state.memory.add_user_message(
        question
    )

    with st.chat_message("user"):
        st.write(question)


    answer = ask_model(
        st.session_state.memory.get_messages()
        )
    

    st.session_state.memory.add_assistant_message(
        answer
    )

    with st.chat_message("assistant"):
        st.write(answer)





