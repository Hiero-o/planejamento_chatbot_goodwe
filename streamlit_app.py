import streamlit as st
from chatbot.memory import Memory
from chatbot.prompt_loader import load_prompt
from tarifacao import EstablishmentRepository, PricingCalculator, SessionRepository

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
    

# ------------------------------------------------------------------ #

#                Guarda página - ui/sidebar.py                       #

if "sidebar_page" not in st.session_state:
            st.session_state.sidebar_page = "Monitoramento"

if "tarifacao_repository" not in st.session_state:
    st.session_state.tarifacao_repository = EstablishmentRepository()
    st.session_state.tarifacao_calculator = PricingCalculator(
        st.session_state.tarifacao_repository
    )
    st.session_state.sessoes_repository = SessionRepository()

if "tarifacao_notice" in st.session_state:
    st.success(st.session_state.pop("tarifacao_notice"))

# ------------------------------------------------------------------ #


tarifacao_repository = st.session_state.tarifacao_repository
tarifacao_calculator = st.session_state.tarifacao_calculator
sessoes_repository = SessionRepository()
st.session_state.sessoes_repository = sessoes_repository
historico_tarifacao = render_sidebar(
    tarifacao_repository,
    tarifacao_calculator,
    sessoes_repository,
)

render_chat()


question = st.chat_input(
    "Digite sua pergunta",
    
)


# ------------------------------------------------------------------ #

if question:


    answer = process_question(
        question,
        st.session_state.memory,
        historico_tarifacao,
        tarifacao_calculator,
        sessoes_repository,
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



        







