import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from src.chain.memoria import get_session_history
from langchain_ollama import ChatOllama
from src.schemas.consultas import (
    ConsultaRecarga,
    ConsultaPotenciaTotal,
    ConsultaCarregadoresDisponiveis,
    ConsultaCarregadoresAtivos,
    ConsultaEnergiaTotal,
)


load_dotenv()

def load_system_prompt():
    caminho = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "prompts",
        "system_prompt_v2.md"
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
            "placeholder",
            "{history}"
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
                "Authorization": f"Bearer {os.getenv('OLLAMA_API_KEY')}"
            }
        },
        temperature=0.3,
        num_predict=1200
    )

    parser = StrOutputParser()

    chain_completa = prompt | llm

    chain = prompt | llm | parser

    chain_com_memoria = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history"
    )

    chain_completa_com_memoria = RunnableWithMessageHistory(
            chain_completa,
            get_session_history,
            input_messages_key="question",
            history_messages_key="history"
        )

    return chain_com_memoria, chain_completa_com_memoria


def build_structured_chain(schema, instrucoes):


    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
        Você é um extrator de dados de operações de eletropostos.

        Sua única função nesta etapa é identificar e estruturar os dados
        necessários para responder à pergunta do usuário.

        O resultado será validado pelo schema Pydantic.

        REGRAS:

        1. Retorne somente os campos necessários para responder à pergunta.
        2. Não retorne campos que não foram solicitados ou que não sejam
        necessários para responder à pergunta.
        3. Nunca invente valores.
        4. Utilize exclusivamente os dados presentes no contexto.
        5. Se um dado não estiver disponível no contexto, não invente.
        6. O identificador do carregador deve seguir o formato charger_XX.
        7. Respeite exatamente os campos definidos pelo schema.
        8. Não responda ao usuário.
        9. Não explique os dados.
        10. Não escreva texto adicional.

        Instruções específicas:
        {instrucoes}
        """),
        (
            "human",
            """
            Contexto dos dados:
            {context}

            Pergunta do usuário:
            {question}
            """
        )
    ])

    llm = ChatOllama(
        model="gemma4:31b-cloud",
        base_url="https://ollama.com",
        client_kwargs={
            "headers": {
                "Authorization": f"Bearer {os.getenv('OLLAMA_API_KEY')}"
            }
        },
        temperature=0.3,
        num_predict=1200,
    )

    structured_llm = llm.with_structured_output(schema)

    chain = prompt | structured_llm

    return chain