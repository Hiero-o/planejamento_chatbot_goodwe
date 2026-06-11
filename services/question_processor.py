import re

from chatbot.llm import ask_model
from services.monitoramento import *
from unidecode import unidecode




def process_question(
        question,
        memory
):

    match = re.search(
        r"charger_(\d+)",
        question.lower()
    )

    contexto = question

    texto = question.lower()

    texto = unidecode(question.lower())

    if match:
        charger_id = f"charger_{match.group(1).zfill(2)}"

        charger = get_charger(charger_id)
        
        if charger:
            contexto = f"""

            Dados atuais do carregador:

            Usuário: {charger["usuario"]}"
            Status: {charger["status"]}"
            Potência: {charger["potencia_kw"]} KW"
            Corrente: {charger["corrente_a"]} A"
            Tensão: {charger["tensao_v"]} V"
            Energia: {charger["energia_kwh"]} KWH"
            Tempo Restante: {charger["tempo_restante_min"]} Min"
            Horario: {charger["horario"]}"
            Tarifa: {charger["tarifa_kwh"]} KWH\n\n"

            Pergunta:
            {question}
            """
            
        # Consultas agregadas

    elif "potencia total" in texto:
        total = get_total_power()

        contexto = f"""
        Potência total da planta: {total} KW

        Pergunta:
        {question}
        """
            

    elif "disponiveis" in texto:
        disponiveis = get_available_chargers()

        contexto = f"""
        Caregadores disponíveis:

        {disponiveis}

        Pergunta:

        {question}
        """
        

    elif "carregadores em uso" in texto:
        ativos = get_active_chargers()

        
        contexto = f"""
            Carregadores em uso:

            {ativos}

            Pergunta:

            {question}

        """
    

    elif "qual a energia total usada?" in texto:
        energia_tot = get_total_energy()

        contexto= f"""
            Total de energia usada: {energia_tot} KWH

            Pergunta:

            {question}

        """

    memory.add_user_message(
        contexto
    )


    answer = ask_model(
        memory.get_messages()
    )

    memory.add_assistant_message(
        answer
    )

    return answer