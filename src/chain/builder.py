import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

load_dotenv()

def load_system_prompt():
    caminho = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "prompts",
        "system_prompt.md"
    )
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return arquivo.read()

def build_chain():

    system_prompt = load_system_prompt()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            system_prompt
        ),
        (
            "human",
            """
            Contexto dos dados:
            {context}
            
            Pergunta do usuario:
            {question}
            """
        )
    ])

    llm = ChatOllama(
        model="gemma4:31b-cloud",
        base_url="https://ollama.com",
        client_kwargs={
            "headers": {
                "Authorization": f"Bearer {os.getenv("OLLAMA_API_KEY")}"
            }
        },
        temperature=0.3,
        num_predict=1200,
    )

    parser = StrOutputParser()

    chain = prompt| llm | parser

    return chain