from services.conhecimento_loader import load_all_documents
import re

from unidecode import unidecode

conhecimento = load_all_documents()


def split_chunks(
        texto,
        tamanho = 1000
):
    
    chunks = []

    for i in range(
        0,
        len(texto),
        tamanho
    ):
        chunks.append(
            texto[i:i+tamanho]
        )
    return chunks


def search_conhecimento(
    question,
    conhecimento
):

    STOPWORDS = [
        "a",
        "o",
        "os",
        "as",
        "de",
        "do",
        "da",
        "dos",
        "das",
        "qual",
        "quais",
        "que",
        "e",
        "sao",
        "um",
        "uma"
    ]

    palavras = [

    p

    for p in re.findall(
        r"[a-zA-Z0-9_]+",
        unidecode(question.lower())
    )

    if p not in STOPWORDS
]

    chunks = split_chunks(
        conhecimento,
        1000
    )

    melhor_chunk = None
    melhor_score = 0
    melhor_pos = None

    for i, chunk in enumerate(chunks):

        score = 0

        chunk_lower = unidecode(
            chunk.lower()
        )

        for palavra in palavras:

            if palavra in chunk_lower:
                score += 1

        if score > melhor_score:

            melhor_score = score
            melhor_chunk = chunk

            melhor_pos = i
            

    if melhor_score < 1:

        return None
    
    resultado = melhor_chunk

    if melhor_pos + 1 < len(chunks):
        resultado += "\n" + chunks[melhor_pos + 1]
    


    return resultado

