import random
import re
from datetime import datetime, timedelta
from decimal import Decimal

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


def _create_random_tariff_session(
        question,
        tarifacao_calculator,
        sessoes_repository,
):
    normalized = unidecode(question.lower())
    match = re.search(
        r"crie um usuario\s+(?:com o nome|chamado)\s*\"?([^\",]+)\"?\s*"
        r"(?:,?\s*e que tenha o carro|,?\s*com o carro|"
        r"\s*que use o veiculo)\s*\"?([^\",]+)\"?",
        normalized,
    )
    if not match or "aleatori" not in normalized or "tarif" not in normalized:
        return None

    usuario_id = match.group(1).strip().title()
    veiculo_id = match.group(2).strip().title()
    establishment = tarifacao_calculator.repository.get_establishment(
        "estabelecimento_01"
    )
    generator = random.Random()
    charger = generator.choice(establishment.carregadores)
    inicio = datetime.now().replace(
        hour=generator.choice([8, 10, 13, 17, 18, 19, 20]),
        minute=generator.choice([0, 15, 30, 45]),
        second=0,
        microsecond=0,
    ) - timedelta(days=generator.randint(0, 7))
    duracao = generator.choice([20, 30, 40, 45, 60, 75, 90])
    potencia = generator.choice([
        charger.potencia_kw,
        charger.potencia_kw * Decimal("0.8"),
        charger.potencia_kw * Decimal("0.9"),
    ])
    bandeira = generator.choice(["verde", "verde", "amarela", "vermelha_1"])
    resultado = tarifacao_calculator.simulate(
        "estabelecimento_01",
        charger.charger_id,
        inicio,
        duracao,
        potencia,
        bandeira,
        usuario_id,
        veiculo_id,
    )
    registro = sessoes_repository.save(resultado)
    return (
        "Usuário e sessão criados com sucesso.\n\n"
        f"- Usuário: {usuario_id}\n"
        f"- Veículo: {veiculo_id}\n"
        f"- Estabelecimento: {establishment.nome}\n"
        f"- Sessão: {registro['session_id']}\n"
        f"- Carregador: {registro['charger_id']}\n"
        f"- Horário: {registro['inicio']}\n"
        f"- Duração: {registro['duracao_minutos']} minutos\n"
        f"- Potência: {registro['potencia_kw']} kW\n"
        f"- Energia estimada: {registro['energia_kwh']} kWh\n"
        f"- Bandeira: {registro['bandeira']}\n"
        f"- Período: {registro['periodo']}\n"
        f"- Custo total: R$ {registro['custo_total']:.2f}\n\n"
        "A sessão foi armazenada no histórico de tarifação desse usuário e veículo."
    )


def process_question(
        question,
    memory,
    historico_tarifacao=None,
    tarifacao_calculator=None,
    sessoes_repository=None,
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

    if tarifacao_calculator and sessoes_repository:
        tariff_result = _create_random_tariff_session(
            question,
            tarifacao_calculator,
            sessoes_repository,
        )
        if tariff_result:
            memory.add_user_message(question)
            memory.add_assistant_message(tariff_result)
            return tariff_result

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
        
    
        
    

    if historico_tarifacao:
        contexto = f"{historico_tarifacao}\n\nPergunta atual:\n{contexto}"

    memory.add_user_message(contexto)

    answer = ask_model(
        memory.get_messages()
    )

    memory.add_assistant_message(
        answer
    )

    

    return answer