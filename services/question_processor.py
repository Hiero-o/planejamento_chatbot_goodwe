import re

import time

from src.guardrails.scope_validator import validar_escopo
from services.charger_parser import extract_charger_id
from unidecode import unidecode
from services.conhecimento_queries import search_conhecimento_context
from services.dynamic_queries import (
    get_charger_context,
    get_total_power_context,
    get_available_charger_context,
    get_active_charger_context,
    get_total_energy_context
)
from services.help import get_help_message
from services.intents import detect_intent
from src.guardrails.moderation import detectar_jailbreak, detectar_seguranca_eletrica
from src.chain.builder import build_chain, build_structured_chain

from src.schemas.consultas import (
    ConsultaRecarga,
    ConsultaPotenciaTotal,
    ConsultaCarregadoresDisponiveis,
    ConsultaCarregadoresAtivos,
    ConsultaEnergiaTotal,
)

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
    Não invente valores."""
)

structured_potencia = build_structured_chain(
    ConsultaPotenciaTotal,
    "Extraia a potência total atual da planta em kW. O campo potencia_total_kw deve receber somente o valor numérico."
)

structured_disponiveis = build_structured_chain(
    ConsultaCarregadoresDisponiveis,
    """
    Extraia a lista de identificadores dos carregadores que estão atualmente disponíveis.

    O campo OBRIGATÓRIO do resultado deve se chamar exatamente:
    carregadores_disponiveis

    Exemplo:
    {"carregadores_disponiveis": ["charger_02", "charger_03"]}
    """
)

structured_ativos = build_structured_chain(
    ConsultaCarregadoresAtivos,
    """
    Extraia a lista de identificadores dos carregadores que estão atualmente em uso.

    O campo OBRIGATÓRIO do resultado deve se chamar exatamente:
    carregadores_ativos

    Exemplo:
    {"carregadores_ativos": ["charger_01", "charger_04"]}
    """
)

structured_energia = build_structured_chain(
    ConsultaEnergiaTotal,
    "Extraia a energia total utilizada pela planta em kWh. O campo energia_total_kwh deve receber somente o valor numérico."
)


def criar_dados_estruturados(contexto, intent):
    if intent == "TOTAL_POWER":
        valor = float(re.search(r"[\d.]+", contexto).group())
        return ConsultaPotenciaTotal(potencia_total_kw=valor)

    if intent == "TOTAL_ENERGY":
        valor = float(re.search(r"[\d.]+", contexto).group())
        return ConsultaEnergiaTotal(energia_total_kwh=valor)

    if intent == "AVAILABLE_CHARGERS":
        encontrados = re.findall(r"charger_\d+", contexto)
        return ConsultaCarregadoresDisponiveis(
            carregadores_disponiveis=encontrados
        )

    if intent == "ACTIVE_CHARGERS":
        encontrados = re.findall(r"charger_\d+", contexto)
        return ConsultaCarregadoresAtivos(
            carregadores_ativos=encontrados
        )

    return None

def formatar_resposta_estruturada(dados):
    if isinstance(dados, ConsultaPotenciaTotal):
        return f"A potência total da planta é de {dados.potencia_total_kw} kW."

    if isinstance(dados, ConsultaEnergiaTotal):
        return f"A energia total utilizada pela planta é de {dados.energia_total_kwh} kWh."

    if isinstance(dados, ConsultaCarregadoresDisponiveis):
        carregadores = ", ".join(dados.carregadores_disponiveis)
        return f"Os carregadores disponíveis são: {carregadores}."

    if isinstance(dados, ConsultaCarregadoresAtivos):
        carregadores = ", ".join(dados.carregadores_ativos)
        return f"Os carregadores em uso são: {carregadores}."

    return None

def process_question(question, session_id, retornar_metricas=False):
    contexto = None
    texto = unidecode(question.lower())
    texto = re.sub(r"[^\w\s]", "", texto)

    # ---------------------------------------------------------
    # Guardrail de escopo
    # ---------------------------------------------------------
    
    resultado_escopo = validar_escopo(question)

    if detectar_jailbreak(question):
        return (
            "Sinto muito, mas não posso atender a essa solicitação. "
            "Não forneço instruções para comprometer a segurança do sistema "
            "ou alterar configurações críticas sem autorização."
        )

    if detectar_seguranca_eletrica(question):
        return (
            "Por razões de segurança, não forneço instruções passo a passo "
            "para instalação elétrica, alteração de fiação, abertura ou "
            "manutenção do carregador. Essas intervenções devem ser realizadas "
            "por profissional habilitado e qualificado."
        )

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

    print("intent detectada:", intent)

    # ---------------------------------------------------------
    # Códigos Modbus determinísticos
    # ---------------------------------------------------------

    RESPOSTAS_MODBUS = {
        "0x0001": """
        0x0001 - Illegal Function

        Este código Modbus indica que o dispositivo recebeu uma
        função ou comando que não suporta.

        Normalmente ocorre quando um sistema tenta executar uma
        operação não implementada pelo carregador.
        """,

        "0x0002": """
        0x0002 - Illegal Data Address

        O endereço Modbus solicitado não existe ou não está
        disponível no equipamento.
        """,

        "0x0003": """
        0x0003 - Illegal Data Value

        O valor enviado ao registrador é inválido ou está fora da faixa permitida.
        """,

        "0x0004": """
        0x0004 - Slave Device Failure

        O carregador encontrou uma falha interna ao processar a solicitação Modbus.
    """
    }
    
    for codigo, resposta in RESPOSTAS_MODBUS.items():
        if codigo in texto:
            return resposta

    # ---------------------------------------------------------
    # Seleção do contexto e do schema
    # ---------------------------------------------------------

    structured_chain = None
    dados_estruturados = None

    if charger_id and intent == "CHARGER_INFO":
        contexto = get_charger_context(charger_id)
        structured_chain = structured_recarga

    elif intent == "TOTAL_POWER":
        contexto = get_total_power_context()
        dados_estruturados = criar_dados_estruturados(contexto, intent)

    elif intent == "AVAILABLE_CHARGERS":
        contexto = get_available_charger_context()
        dados_estruturados = criar_dados_estruturados(contexto, intent)

    elif intent == "ACTIVE_CHARGERS":
        contexto = get_active_charger_context()
        dados_estruturados = criar_dados_estruturados(contexto, intent)

    elif intent == "TOTAL_ENERGY":
        contexto = get_total_energy_context()
        dados_estruturados = criar_dados_estruturados(contexto, intent)

    elif intent == "HELP":
        return get_help_message()

    # ---------------------------------------------------------
    # Busca na documentação
    # ---------------------------------------------------------

    if contexto is None:
        trecho = search_conhecimento_context(question)

        if trecho:
            contexto = f"""
            Você é um assistente técnico especializado.

            Utilize prioritariamente o contexto fornecido.

            Quando houver uma descrição técnica no contexto,
            explique-a de forma simples e profissional.

            Não invente informações que não estejam no contexto.

            Se o contexto não possuir informações suficientes,
            responda:

            "Não encontrei essa informação na documentação disponível."

            Contexto:

            {trecho}

            Pergunta:

            {question}
            """
        else:
            contexto = question
    
    if dados_estruturados:
        resposta = formatar_resposta_estruturada(dados_estruturados)

        if retornar_metricas:
            return {
                "resposta": resposta,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0
            }

        return resposta

    # ---------------------------------------------------------
    # Structured Output
    # ---------------------------------------------------------

    if structured_chain:
        inicio = time.perf_counter()

        dados = structured_chain.invoke({
            "context": contexto,
            "question": question
        })

        print(
            f"[TEMPO] structured_chain: "
            f"{time.perf_counter() - inicio:.3f}s"
        )

        # -----------------------------------------------------
        # Respostas que podem ser geradas diretamente
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # ConsultaRecarga continua usando a LLM para resposta
        # natural
        # -----------------------------------------------------

        contexto = dados.model_dump_json()

    # ---------------------------------------------------------
    # Chamada final da LLM
    # ---------------------------------------------------------

    inicio = time.perf_counter()

    resposta_llm = chain_completa.invoke(
        {
            "context": contexto,
            "question": question
        },
        config={
            "configurable": {
                "session_id": session_id
            }
        }
    )

    print(
        f"[TEMPO] chain final: "
        f"{time.perf_counter() - inicio:.3f}s"
    )

    # ---------------------------------------------------------
    # Retorno das métricas
    # ---------------------------------------------------------

    if retornar_metricas:
        metricas = resposta_llm.usage_metadata

        return {
            "resposta": resposta_llm.content,
            "input_tokens": metricas["input_tokens"],
            "output_tokens": metricas["output_tokens"],
            "total_tokens": metricas["total_tokens"]
        }

    return resposta_llm.content