import re

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
from src.chain.builder import build_chain, build_structured_chain

from src.schemas.consultas import (
    ConsultaRecarga,
    ConsultaPotenciaTotal,
    ConsultaCarregadoresDisponiveis,
    ConsultaCarregadoresAtivos,
    ConsultaEnergiaTotal,
)

chain = build_chain()

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



def process_question(
        question,
        session_id,
        retornar_metricas=False
):
    
    contexto = None

    charger_id = extract_charger_id(question)

    texto = unidecode(question.lower())

    texto = re.sub(
        r"[^\w\s]",
        "",
        texto
    )
    

    intent = detect_intent(texto)

    print("intent detectada:", intent)

    if "0x0001" in texto:

        return """
        0x0001 - Illegal Function

        Este código Modbus indica que o dispositivo recebeu uma
        função ou comando que não suporta.

        Normalmente ocorre quando um sistema tenta executar uma
        operação não implementada pelo carregador.
        """
    

    if "0x0002" in texto:

        return """
        0x0002 - Illegal Data Address

        O endereço Modbus solicitado não existe ou não está
        disponível no equipamento.
        """

    if "0x0003" in texto:

        return """
        0x0003 - Illegal Data Value

        O valor enviado ao registrador é inválido ou está fora da faixa permitida.
        """

    if "0x0004" in texto:

        return """
        0x0004 - Slave Device Failure

        O carregador encontrou uma falha interna ao processar a solicitação Modbus.

        """

    structured_chain = None

    if charger_id:
        contexto = get_charger_context(charger_id)   
        structured_chain = structured_recarga   
            
    # Consultas agregadas

    elif intent == "TOTAL_POWER":
        contexto = get_total_power_context()
        structured_chain = structured_potencia


    elif intent ==  "AVAILABLE_CHARGERS":
        contexto = get_available_charger_context()
        structured_chain = structured_disponiveis

        
    elif intent == "ACTIVE_CHARGERS":
        contexto = get_active_charger_context()
        structured_chain = structured_ativos


    elif intent == "TOTAL_ENERGY":
        contexto = get_total_energy_context()
        structured_chain = structured_energia

    

    
    elif intent == "HELP":
        get_help_message()

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

        
    
    if structured_chain:

        dados = structured_chain.invoke({
            "context": contexto,
            "question": question
        })
        print("\n===== STRUCTURED OUTPUT =====")
        print(dados)
        print(dados.model_dump())
        print("==============================\n")

        answer = chain.invoke(
            {
                "context": dados.model_dump_json(),
                "question": question
            },
            config={
                "configurable": {
                    "session_id": session_id
                }
            }
        )


        return answer