from chatbot.llm import ask_model
from chatbot.memory import Memory
from chatbot.prompt_loader import load_prompt
from services.monitoramento import get_charger
import re

system_prompt = load_prompt()

memory = Memory(system_prompt)

print("GurAI iniciado.")
print("Digite 'sair' para encerrar.\n")

while True:

    question = input("Você: ")

    if question.lower() == "sair":
        break


    match = re.search(
        r"charger_(\d+)",
        question.lower()
    )

    if match:
        charger_id = f"charger_{match.group(1).zfill(2)}"

        charger = get_charger(charger_id)

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
        """
        

        memory.add_user_message(
            f"""
            Dados do carregador:

            {contexto}

            Pergunta:
            {question}
            """
        )
    else:
        memory.add_user_message(question)

    answer = ask_model(
        memory.get_messages()
    )

    memory.add_assistant_message(answer)

    print(f"\nGurAI: {answer}\n")