import re

from chatbot.llm import ask_model
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


def process_question(
        question,
        memory,
        retornar_metricas=False
):
    
    contexto = None

    match = re.search(
        r"charger_(\d+)",
        question.lower()
    )

    texto = unidecode(question.lower())

    texto = re.sub(
        r"[^\w\s]",
        "",
        texto
    )

    intent = detect_intent(texto)

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
    if match:
        charger_id = f"charger_{match.group(1).zfill(2)}"

        contexto = get_charger_context(charger_id)      
            
    # Consultas agregadas

    elif intent == "TOTAL_POWER":
        contexto = get_total_power_context()

    elif intent ==  "AVAILABLE_CHARGERS":
        contexto = get_available_charger_context()
        
    elif intent == "ACTIVE_CHARGERS":
        contexto = get_active_charger_context()

    elif intent == "TOTAL_ENERGY":
        contexto = get_total_energy_context()

    
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
        
    
    memory.add_user_message(
        f"""
    Contexto dos dados:

    {contexto}

    Pergunta do usuário:

    {question}
    """
    )

    answer = ask_model(
    memory.get_messages(),
    retornar_metricas=retornar_metricas
    )

    return answer