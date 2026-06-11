import re

from chatbot.llm import ask_model
from service.monitoramento import (
    get_charger
)

def process_question(
        question,
        memory
):
    
    memory.add_user_message(
        question
    )

    match = re.search(
        r"charger_(\d+)",
        question.lower()
    )

    if match:
        charger_id = (
            f"charger_",
            f"{match.group(1).zfill(2)}"
        )

        charger = get_charger(
            charger_id
        )

        answer = ask_model(
            memory.get_messages()
        )

        memory.add_assistant_message(
            answer
        )

        return answer