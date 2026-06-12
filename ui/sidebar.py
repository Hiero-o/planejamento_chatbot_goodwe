
import streamlit as st
from services.monitoramento import *



def linha():
    st.write("----------------------")

potencia = get_total_power()
ativos = get_available_chargers()
energia = get_total_energy()
carregador_em_uso = get_active_chargers()






def render_sidebar():

    

    
    with st.sidebar:


        st.title("Perguntas realizadas")

        for message in st.session_state.chat_history[-10:]:
            if message["role"] == "user":

                st.write(
                    message["content"]
                )

        linha()

        st.title("Painel")

        if st.button("Monitoramento"):
            st.session_state.sidebar_page = "Monitoramento"
        if st.button ("Carregadores"):
            st.session_state.sidebar_page = "Carregadores"
        

        st.divider()

        if st.session_state.sidebar_page == "Monitoramento":



            st.title("Monitoramento")

            

            st.metric(
                label="Potência Total",
                value=f"{potencia} KW"
            )

            

            st.metric(
                label="Carregadores ativos",
                value=len(carregador_em_uso)
            )

            

            st.metric(
                label="Carregadores disponíveis",
                value=len(ativos)
            )

            


            st.metric(
                label="Total de energia usada",
                value=f"{energia} KWH"
            )

            

        elif st.session_state.sidebar_page == "Carregadores":
        
            chargers = get_all_chargers()

            st.title("⚡ Carregadores")

            for charger_id, dados in chargers.items():
                if dados['status'] == "Disponível":
                    st.markdown(
                    f" {charger_id} - {dados['status']} 🟢"
                    )
                elif dados['status'] == "Carregando":
                    st.markdown(
                        f" {charger_id} - {dados['status']} 🟡"
                    )
                elif dados['status'] == "Desconectado":
                    st.markdown(
                        f" {charger_id} - {dados['status']} 🔴"
                    )

            linha()

            pagina = st.radio(
                "Menu de Carregadores",
                list(chargers.keys()),
                
            )

            st.subheader(f"🔌 Carregador: {pagina}")

            dados = chargers[pagina]

        
            st.markdown(
            f"""

    **Dados do {pagina}**\n
    Usuário: {dados["usuario"]}\n
    Status: {dados["status"]}
    Potência: {dados["potencia_kw"]} KW
    Corrente: {dados["corrente_a"]} A
    Tensão: {dados["tensao_v"]} V
    Energia: {dados["energia_kwh"]} KWH
    Tempo Restante: {dados["tempo_restante_min"]} Min
    Horario: {dados["horario"]}
    Tarifa: {dados["tarifa_kwh"]} KWH\n"
            
            """
            )
            linha()