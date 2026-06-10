import streamlit as st
from chatbot.llm import ask_model
from chatbot.memory import Memory
from chatbot.prompt_loader import load_prompt
from services.monitoramento import *

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


question = st.chat_input(
    "Digite sua pergunta",
    
)


# ------------------------------------------------------------------ #

if question:

    st.session_state.memory.add_user_message(
        question
    )

    with st.chat_message("user"):
        st.write(question)
    
    st.session_state.chat_history.append(
        {
        "role": "user",
        "content": question
        }
    ) 


    answer = ask_model(
        st.session_state.memory.get_messages()
        )
    

    st.session_state.memory.add_assistant_message(
        answer
    )

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):
        st.write(answer)


with st.sidebar:

    st.title("Perguntas realizadas")

    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.write(
                message["content"]
            )
        







