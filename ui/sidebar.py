
import streamlit as st
from datetime import datetime, time
from chatbot.memory import Memory
from chatbot.prompt_loader import load_prompt
from tarifacao import EstablishmentRepository, PricingCalculator, SessionRepository



def linha():
    st.write("----------------------")

def render_sidebar(
    tarifacao_repository: EstablishmentRepository,
    tarifacao_calculator: PricingCalculator,
    sessoes_repository: SessionRepository,
):

    with st.sidebar:

        if st.sidebar.button("Nova Conversa", use_container_width=True):

            system_prompt = load_prompt()

            st.session_state.memory = Memory(

                system_prompt

            )
            st.session_state.chat_history = []

            st.session_state.sidebar_page = "Monitoramento"

            st.rerun()


        st.title("Painel")

        if st.button("Monitoramento", use_container_width=True):
            st.session_state.sidebar_page = "Monitoramento"

        if st.button("Tarifação", use_container_width=True):
            st.session_state.sidebar_page = "Tarifação"
        
        linha()
        
        st.title("Perguntas realizadas")

        for message in st.session_state.chat_history[-10:]:
            if message["role"] == "user":

                st.write(
                    message["content"]
                )

        st.divider()

        if st.session_state.sidebar_page == "Monitoramento":
            estabelecimentos = tarifacao_repository.list_establishments()
            estabelecimento_ids = [item.estabelecimento_id for item in estabelecimentos]
            historico_tarifacao = None

            st.subheader("Resumo de tarifação")
            if estabelecimento_ids:
                estabelecimento_id = st.selectbox(
                    "Estabelecimento",
                    estabelecimento_ids,
                    key="tarifacao_estabelecimento",
                )
                usuario_id = st.text_input(
                    "Usuário",
                    value="usuario_01",
                    key="tarifacao_usuario",
                ).strip() or "anonimo"
                veiculo_id = st.text_input(
                    "Veículo",
                    value="carro_01",
                    key="tarifacao_veiculo",
                ).strip() or "nao informado"
                sessoes = sorted(
                    sessoes_repository.find(estabelecimento_id, usuario_id, veiculo_id),
                    key=lambda sessao: sessao["inicio"],
                    reverse=True,
                )
                historico_tarifacao = sessoes_repository.summary_for_gurai(
                    estabelecimento_id,
                    usuario_id,
                    veiculo_id,
                )
                total_cost = sum(sessao["custo_total"] for sessao in sessoes)
                total_energy = sum(sessao["energia_kwh"] for sessao in sessoes)
                metrics = st.columns(2)
                metrics[0].metric("Recargas", len(sessoes))
                metrics[1].metric("Custo acumulado", f"R$ {total_cost:.2f}")
                st.caption(f"Energia acumulada: {total_energy:.3f} kWh")

                if sessoes:
                    ultima = sessoes[0]
                    st.info(
                        f"Última recarga: {ultima['inicio']} | "
                        f"{ultima['energia_kwh']} kWh | R$ {ultima['custo_total']}"
                    )
                    with st.expander("Recargas recentes"):
                        st.dataframe(
                            [
                                {
                                    "Data": sessao["inicio"],
                                    "Duração": f"{sessao['duracao_minutos']} min",
                                    "Energia": f"{sessao['energia_kwh']} kWh",
                                    "Custo": f"R$ {sessao['custo_total']}",
                                }
                                for sessao in sessoes[:5]
                            ],
                            use_container_width=True,
                            hide_index=True,
                        )
                else:
                    st.caption("Nenhuma recarga registrada para este usuário e veículo.")
            else:
                st.warning("Nenhum estabelecimento cadastrado.")

            return historico_tarifacao

        if st.session_state.sidebar_page == "Tarifação":
            estabelecimentos = tarifacao_repository.list_establishments()
            estabelecimento_ids = [item.estabelecimento_id for item in estabelecimentos]

            st.title("Tarifação")
            if not estabelecimento_ids:
                st.warning("Nenhum estabelecimento cadastrado.")
                return None

            estabelecimento_id = st.selectbox(
                "Estabelecimento",
                estabelecimento_ids,
                key="tarifacao_estabelecimento",
            )
            usuario_id = st.text_input(
                "Usuário",
                value="usuario_01",
                key="tarifacao_usuario",
            ).strip() or "anonimo"
            veiculo_id = st.text_input(
                "Veículo",
                value="carro_01",
                key="tarifacao_veiculo",
            ).strip() or "nao informado"

            sessoes = sorted(
                sessoes_repository.find(estabelecimento_id, usuario_id, veiculo_id),
                key=lambda sessao: sessao["inicio"],
                reverse=True,
            )
            historico_tarifacao = sessoes_repository.summary_for_gurai(
                estabelecimento_id,
                usuario_id,
                veiculo_id,
            )
            st.metric("Sessões encontradas", len(sessoes))
            if sessoes:
                total_cost = sum(sessao["custo_total"] for sessao in sessoes)
                total_energy = sum(sessao["energia_kwh"] for sessao in sessoes)
                st.metric("Custo acumulado", f"R$ {total_cost:.2f}")
                st.metric("Energia acumulada", f"{total_energy:.3f} kWh")

            with st.expander("Sessões registradas", expanded=True):
                if sessoes:
                    st.dataframe(
                        [
                            {
                                "ID": sessao["session_id"],
                                "Data": sessao["inicio"],
                                "Carregador": sessao["charger_id"],
                                "Minutos": sessao["duracao_minutos"],
                                "kWh": sessao["energia_kwh"],
                                "Bandeira": sessao["bandeira"],
                                "Custo (R$)": sessao["custo_total"],
                            }
                            for sessao in sessoes[:20]
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("Nenhuma sessão registrada para este filtro.")

            with st.expander("Simular sessão"):
                estabelecimento = tarifacao_repository.get_establishment(estabelecimento_id)
                charger_ids = [charger.charger_id for charger in estabelecimento.carregadores]
                with st.form("formulario_sessao"):
                    charger_id = st.selectbox("Carregador", charger_ids)
                    charger = next(item for item in estabelecimento.carregadores if item.charger_id == charger_id)
                    data_sessao = st.date_input("Data", value=datetime.now().date())
                    horario_sessao = st.time_input("Horário", value=time(18, 0))
                    duracao = st.number_input("Duração (minutos)", min_value=1, value=40, step=5)
                    potencia = st.number_input("Potência (kW)", min_value=0.0, value=float(charger.potencia_kw), step=0.1)
                    bandeira = st.selectbox("Bandeira", ["verde", "amarela", "vermelha_1", "vermelha_2"])
                    registrar = st.form_submit_button("Calcular e registrar")

                if registrar:
                    resultado = tarifacao_calculator.simulate(
                        estabelecimento_id,
                        charger_id,
                        datetime.combine(data_sessao, horario_sessao),
                        int(duracao),
                        potencia,
                        bandeira,
                        usuario_id,
                        veiculo_id,
                    )
                    sessoes_repository.save(resultado)
                    st.session_state.tarifacao_notice = (
                        f"Sessão registrada para {usuario_id}/{veiculo_id}. "
                        f"Custo: R$ {resultado.custo_total}"
                    )
                    st.rerun()

            if st.button("Gerar 10 sessões demonstrativas", key="gerar_sessoes_demo"):
                sessoes_geradas = sessoes_repository.generate_demo_sessions(
                    tarifacao_calculator,
                    estabelecimento_id,
                    [(usuario_id, veiculo_id)],
                    count=10,
                    seed=42,
                )
                st.session_state.tarifacao_notice = (
                    f"{len(sessoes_geradas)} sessões demonstrativas adicionadas ao "
                    f"histórico de {usuario_id}/{veiculo_id}."
                )
                st.rerun()

            with st.expander("Contexto enviado ao GurAI"):
                st.text(historico_tarifacao)
            return historico_tarifacao

    return None