import logging
import re
import time

from unidecode import unidecode

from src.guardrails.scope_validator import validar_escopo
from services.charger_parser import extract_charger_id
from src.rag.context_builder import build_documentation_context
from services.dynamic_queries import (
    get_charger_context,
    get_total_power_context,
    get_available_charger_context,
    get_active_charger_context,
    get_total_energy_context,
)
from services.help import get_help_message
from services.intents import detect_intent
from src.guardrails.moderation import (
    detectar_jailbreak,
    detectar_seguranca_eletrica,
)
from src.chain.builder import build_chain, build_structured_chain
from src.schemas.consultas import (
    ConsultaRecarga,
    ConsultaPotenciaTotal,
    ConsultaCarregadoresDisponiveis,
    ConsultaCarregadoresAtivos,
    ConsultaEnergiaTotal,
)
from services.user_sessions import (
    is_personal_session_question,
    build_user_sessions_context,
)


# ---------------------------------------------------------
# Construção das chains
# ---------------------------------------------------------

chain, chain_completa = build_chain()


structured_recarga = build_structured_chain(
    ConsultaRecarga,
    """Use exatamente os nomes dos campos do schema.

    Mapeamentos:
    - potência → potencia_kw
    - corrente → corrente_a
    - tensão → tensao_v
    - energia → energia_kwh
    - tempo restante → tempo_restante_min
    - tarifa → tarifa_kwh
    - usuário → usuario
    - status → status
    - carregador → carregador

    Extraia somente os campos necessários para responder à pergunta.
    Não invente valores.""",
)


structured_potencia = build_structured_chain(
    ConsultaPotenciaTotal,
    "Extraia a potência total atual da planta em kW. "
    "O campo potencia_total_kw deve receber somente o valor numérico.",
)


structured_disponiveis = build_structured_chain(
    ConsultaCarregadoresDisponiveis,
    """
    Extraia a lista de identificadores dos carregadores
    que estão atualmente disponíveis.

    O campo OBRIGATÓRIO do resultado deve se chamar exatamente:
    carregadores_disponiveis

    Exemplo:
    {"carregadores_disponiveis": ["charger_02", "charger_03"]}
    """,
)


structured_ativos = build_structured_chain(
    ConsultaCarregadoresAtivos,
    """
    Extraia a lista de identificadores dos carregadores
    que estão atualmente em uso.

    O campo OBRIGATÓRIO do resultado deve se chamar exatamente:
    carregadores_ativos

    Exemplo:
    {"carregadores_ativos": ["charger_01", "charger_04"]}
    """,
)


structured_energia = build_structured_chain(
    ConsultaEnergiaTotal,
    "Extraia a energia total utilizada pela planta em kWh. "
    "O campo energia_total_kwh deve receber somente o valor numérico.",
)


# ---------------------------------------------------------
# Dados estruturados
# ---------------------------------------------------------

def criar_dados_estruturados(contexto, intent):
    contexto = contexto or ""

    if intent == "TOTAL_POWER":
        match = re.search(r"[\d.]+", contexto)

        if not match:
            return None

        valor = float(match.group())

        return ConsultaPotenciaTotal(
            potencia_total_kw=valor
        )

    if intent == "TOTAL_ENERGY":
        match = re.search(r"[\d.]+", contexto)

        if not match:
            return None

        valor = float(match.group())

        return ConsultaEnergiaTotal(
            energia_total_kwh=valor
        )

    if intent == "AVAILABLE_CHARGERS":
        encontrados = re.findall(
            r"charger_\d+",
            contexto,
        )

        return ConsultaCarregadoresDisponiveis(
            carregadores_disponiveis=encontrados
        )

    if intent == "ACTIVE_CHARGERS":
        encontrados = re.findall(
            r"charger_\d+",
            contexto,
        )

        return ConsultaCarregadoresAtivos(
            carregadores_ativos=encontrados
        )

    return None


def formatar_resposta_estruturada(dados):
    if isinstance(dados, ConsultaPotenciaTotal):
        return (
            f"A potência total da planta é de "
            f"{dados.potencia_total_kw} kW."
        )

    if isinstance(dados, ConsultaEnergiaTotal):
        return (
            f"A energia total utilizada pela planta é de "
            f"{dados.energia_total_kwh} kWh."
        )

    if isinstance(dados, ConsultaCarregadoresDisponiveis):
        carregadores = ", ".join(
            dados.carregadores_disponiveis
        )

        return (
            f"Os carregadores disponíveis são: "
            f"{carregadores}."
        )

    if isinstance(dados, ConsultaCarregadoresAtivos):
        carregadores = ", ".join(
            dados.carregadores_ativos
        )

        return (
            f"Os carregadores em uso são: "
            f"{carregadores}."
        )

    return None


# ---------------------------------------------------------
# Processamento principal
# ---------------------------------------------------------

def process_question(
    question,
    session_id,
    retornar_metricas=False,
    user_sessions=None,
    user_sessions_summary=None,
):
    contexto = None

    texto = unidecode(question.lower())
    texto = re.sub(r"[^\w\s]", "", texto)

    # ---------------------------------------------------------
    # Guardrail de escopo
    # ---------------------------------------------------------

    resultado_escopo = validar_escopo(question)

    # ---------------------------------------------------------
    # Proteção contra jailbreak
    # ---------------------------------------------------------

    if detectar_jailbreak(question):
        return (
            "Sinto muito, mas não posso atender a essa solicitação. "
            "Não forneço instruções para comprometer a segurança do sistema "
            "ou alterar configurações críticas sem autorização."
        )

    # ---------------------------------------------------------
    # Segurança elétrica
    # ---------------------------------------------------------

    if detectar_seguranca_eletrica(question):
        return (
            "Por razões de segurança, não forneço instruções passo a passo "
            "para instalação elétrica, alteração de fiação, abertura ou "
            "manutenção do carregador. Essas intervenções devem ser realizadas "
            "por profissional habilitado e qualificado."
        )

    # ---------------------------------------------------------
    # Consultas às sessões pessoais do usuário autenticado
    # ---------------------------------------------------------

    if is_personal_session_question(question):
        try:
            sessoes = user_sessions or []
            resumo_sessoes = user_sessions_summary or {}

            if user_sessions_summary is None:
                logging.warning(
                    "O resumo das sessões não foi recebido pela API. "
                    "Tentando montar o contexto com os dados disponíveis."
                )

            contexto_usuario = build_user_sessions_context(
                sessoes,
                resumo_sessoes,
            )

            inicio = time.perf_counter()

            resposta_llm = chain_completa.invoke(
                {
                    "context": contexto_usuario,
                    "question": question,
                },
                config={
                    "configurable": {
                        "session_id": session_id,
                    }
                },
            )

            print(
                "[TEMPO] Consulta de sessões pessoais: "
                f"{time.perf_counter() - inicio:.3f}s"
            )

            if retornar_metricas:
                metricas = (
                    getattr(resposta_llm, "usage_metadata", None)
                    or {}
                )

                return {
                    "resposta": resposta_llm.content,
                    "input_tokens": metricas.get(
                        "input_tokens", 0
                    ),
                    "output_tokens": metricas.get(
                        "output_tokens", 0
                    ),
                    "total_tokens": metricas.get(
                        "total_tokens", 0
                    ),
                }

            return resposta_llm.content

        except Exception:
            logging.exception(
                "Erro ao consultar as sessões do usuário no GurAI"
            )

            return (
                "Não consegui consultar os dados das suas sessões "
                "de carregamento neste momento. Tente novamente."
            )

    # ---------------------------------------------------------
    # Validação de escopo para as demais perguntas
    # ---------------------------------------------------------

    if not resultado_escopo["permitido"]:
        return (
            "Essa solicitação está fora do escopo de atuação do GurAI. "
            "Posso ajudar com informações sobre os carregadores, "
            "monitoramento e equipamentos GoodWe disponíveis na base."
        )

    # ---------------------------------------------------------
    # Identificação da pergunta
    # ---------------------------------------------------------

    charger_id = extract_charger_id(question)
    intent = detect_intent(texto)

    print("Intent detectada:", intent)

    # ---------------------------------------------------------
    # Seleção do contexto e do schema
    # ---------------------------------------------------------

    structured_chain = None
    dados_estruturados = None

    if charger_id and intent == "CHARGER_INFO":
        contexto = get_charger_context(charger_id)

        # Se o carregador não existe nos dados operacionais, não tente
        # extrair uma ConsultaRecarga vazia com o modelo estruturado.
        # Isso evita ValidationError quando o schema exige "carregador".
        if not contexto:
            logging.info(
                "Não há dados operacionais disponíveis para o carregador %s",
                charger_id,
            )
            return (
                f"Não encontrei dados operacionais para o carregador {charger_id}. "
                "Por isso, não consigo confirmar sua potência, corrente, tensão ou "
                "outros dados específicos. Verifique se o identificador está correto "
                "ou consulte os dados disponíveis na plataforma."
            )

        structured_chain = structured_recarga

    elif intent == "TOTAL_POWER":
        contexto = get_total_power_context()

        dados_estruturados = criar_dados_estruturados(
            contexto,
            intent,
        )

    elif intent == "AVAILABLE_CHARGERS":
        contexto = get_available_charger_context()

        dados_estruturados = criar_dados_estruturados(
            contexto,
            intent,
        )

    elif intent == "ACTIVE_CHARGERS":
        contexto = get_active_charger_context()

        dados_estruturados = criar_dados_estruturados(
            contexto,
            intent,
        )

    elif intent == "TOTAL_ENERGY":
        contexto = get_total_energy_context()

        dados_estruturados = criar_dados_estruturados(
            contexto,
            intent,
        )

    elif intent == "HELP":
        return get_help_message()

    # ---------------------------------------------------------
    # Busca na documentação
    # ---------------------------------------------------------

    if contexto is None:
        trecho = build_documentation_context(question)

        if trecho:
            contexto = trecho

        else:
            contexto = (
                "Nenhum trecho relevante na documentação foi recuperado "
                "para esta pergunta. Não invente informações sem fontes. "
                "Se não houver evidências suficientes no contexto ou no "
                "histórico relevante, informe que a informação não foi "
                "encontrada na documentação disponível."
            )

    # ---------------------------------------------------------
    # Respostas estruturadas determinísticas
    # ---------------------------------------------------------

    if dados_estruturados:
        resposta = formatar_resposta_estruturada(
            dados_estruturados
        )

        if retornar_metricas:
            return {
                "resposta": resposta,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            }

        return resposta

    # ---------------------------------------------------------
    # Structured Output
    # ---------------------------------------------------------

    if structured_chain:
        inicio = time.perf_counter()

        dados = structured_chain.invoke(
            {
                "context": contexto,
                "question": question,
            }
        )

        print(
            "[TEMPO] structured_chain: "
            f"{time.perf_counter() - inicio:.3f}s"
        )

        if isinstance(dados, ConsultaPotenciaTotal):
            return (
                f"A potência total da planta é de "
                f"{dados.potencia_total_kw} kW."
            )

        if isinstance(dados, ConsultaEnergiaTotal):
            return (
                f"A energia total utilizada pela planta é de "
                f"{dados.energia_total_kwh} kWh."
            )

        if isinstance(dados, ConsultaCarregadoresDisponiveis):
            carregadores = ", ".join(
                dados.carregadores_disponiveis
            )

            return (
                f"Os carregadores disponíveis são: "
                f"{carregadores}."
            )

        if isinstance(dados, ConsultaCarregadoresAtivos):
            carregadores = ", ".join(
                dados.carregadores_ativos
            )

            return (
                f"Os carregadores em uso são: "
                f"{carregadores}."
            )

        # ConsultaRecarga continua usando a LLM
        # para produzir uma resposta em linguagem natural.
        contexto = dados.model_dump_json()

    # ---------------------------------------------------------
    # Chamada final da LLM
    # ---------------------------------------------------------

    inicio = time.perf_counter()

    resposta_llm = chain_completa.invoke(
        {
            "context": contexto,
            "question": question,
        },
        config={
            "configurable": {
                "session_id": session_id,
            }
        },
    )

    print(
        "[TEMPO] chain final: "
        f"{time.perf_counter() - inicio:.3f}s"
    )

    # ---------------------------------------------------------
    # Retorno das métricas
    # ---------------------------------------------------------

    if retornar_metricas:
        metricas = (
            getattr(resposta_llm, "usage_metadata", None)
            or {}
        )

        return {
            "resposta": resposta_llm.content,
            "input_tokens": metricas.get("input_tokens", 0),
            "output_tokens": metricas.get("output_tokens", 0),
            "total_tokens": metricas.get("total_tokens", 0),
        }

    return resposta_llm.content