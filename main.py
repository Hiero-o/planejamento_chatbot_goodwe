from chatbot.llm import ask_model
from chatbot.memory import Memory
from chatbot.prompt_loader import load_prompt

system_prompt = load_prompt()

memory = Memory(system_prompt)

print("GurAI iniciado.")
print("Digite 'sair' para encerrar.\n")

while True:

    question = input("Você: ")

    if question.lower() == "sair":
        break

    memory.add_user_message(question)

    answer = ask_model(
        memory.get_messages()
    )

    memory.add_assistant_message(answer)

    print(f"\nGurAI: {answer}\n")