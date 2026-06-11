
import streamlit as st
from services.monitoramento import *

def linha():
    st.write("----------------------")

potencia = get_total_power()
ativos = get_available_chargers()
energia = get_total_energy()
carregador_em_uso = get_active_chargers()

chargers = get_all_chargers()

    

def render_sidebar():
    with st.sidebar:

        st.title("Perguntas realizadas")

        for message in st.session_state.chat_history[-10:]:
            if message["role"] == "user":

                st.write(
                    message["content"]
                )
        linha()


        st.title("Monitoramento")

        linha()

        st.metric(
            label="Potência Total",
            value=f"{potencia} KW"
        )

        linha()

        st.metric(
            label="Carregadores ativos",
            value=len(carregador_em_uso)
        )

        linha()

        st.metric(
            label="Carregadores disponíveis",
            value=len(ativos)
        )

        linha()


        st.metric(
            label="Total de energia usada",
            value=f"{energia} KWH"
        )

        linha()

        st.title("Carregadores")

        for i in range(len(chargers)):

            if st.button(f"CHARGER_0{i + 1}"):
                st.session_state.sidebar_page = "Carregadores"

    

        if st.button("Voltar"):
            st.session_state.sidebar_page = "Monitoramento"

       # for charger_id, dados in chargers.items():
        #    st.write(
        #        f"{charger_id} - {dados['status']}"
        #    )

