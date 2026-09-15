import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_classic.memory import ConversationTokenBufferMemory

load_dotenv()


def criar_memoria():
    llm = ChatOllama(
        model="gemma4:31b-cloud",
        base_url="https://ollama.com",
        client_kwargs={
            "headers": {
                "Authorization": f"Bearer {os.getenv('OLLAMA_API_KEY')}"
            }
        },
        temperature=0.3,
        num_predict=1200
    )

    return ConversationTokenBufferMemory(
        llm=llm,
        max_token_limit=1000,
        return_messages=True
    )

memorias = {}

def get_session_history(session_id):
    if session_id not in memorias:
        memorias[session_id] = criar_memoria()

    return memorias[session_id].chat_memory