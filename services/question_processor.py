import re

from chatbot.llm import ask_model
from services.monitoramento import *
from unidecode import unidecode
from services.conhecimento_search import search_conhecimento
from services.conhecimento_loader import load_all_documents
import streamlit as st

from services.intents import detect_intent

conhecimento = load_all_documents()

termos_tecnicos = [

    "erro",
    "modbus",
    "potencia",
    "corrente",
    "tensao",
    "rfid",
    "ocpp",
    "charger",
    "carregador",
    "energia"
]


def process_question(
        question,
        memory
):
    
    contexto = None

    match = re.search(
        r"charger_(\d+)",
        question.lower()
    )


    texto = question.lower()

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

    elif intent == "TOTAL_POWER":
        total = get_total_power()

        contexto = f"""
        Potência total da planta: {total} KW

        Pergunta:
        {question}
        """
            

    elif intent ==  "AVAILABLE_CHARGERS":
        disponiveis = get_available_chargers()

        contexto = f"""
        Caregadores disponíveis:

        {disponiveis}

        Pergunta:

        {question}
        """
        

    elif intent == "ACTIVE_CHARGERS":
        ativos = get_active_chargers()

        
        contexto = f"""
            Carregadores em uso:

            {ativos}

            Pergunta:

            {question}

        """
    

    elif intent == "TOTAL_ENERGY":
        energia_tot = get_total_energy()

        contexto= f"""
            Total de energia usada: {energia_tot} KWH

            Pergunta:

            {question}

        """
    
    elif intent == "HELP":
        return """
        Posso ajudar com:

        ⚡ Status dos carregadores
        ⚡ Potência total da planta
        ⚡ Energia consumida
        ⚡ Carregadores disponíveis
        ⚡ Códigos de erro
        ⚡ Informações dos manuais
        ⚡ Informações Modbus

        Exemplos:

        • Como está o charger_01?

        • Qual a potência total da planta?

        • Quais carregadores estão disponíveis?

        • Qual a energia total utilizada?

        • O que significa o erro 0x0001?

        • Qual a potência nominal do GW22K-HCA-20?
        
        """

    pergunta_tecnica = any(
        termo in texto
        for termo in termos_tecnicos
    )

    
    if contexto is None:

        trecho = search_conhecimento(
            question,
            conhecimento
        )

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
            
        elif pergunta_tecnica:
            return """Não encontrei essa informação na documentação disponível"""
        else:
            contexto = question
        
    
        
    

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