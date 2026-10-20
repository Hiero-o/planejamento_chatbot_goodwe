
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.rag.retriever import create_retriever


def main():
    pergunta = (
        "Qual é a potência máxima de carregamento do "
        "GW22K-HCA-20? Ela é necessariamente igual à "
        "potência nominal de saída?"
    )

    retriever, provider = create_retriever(
        k=10,
        candidate_k=24,
    )

    documentos = retriever.invoke(pergunta)

    print("=" * 70)
    print("DIAGNÓSTICO DO RETRIEVER — OBC")
    print(f"Provider: {provider}")
    print(f"Resultados encontrados: {len(documentos)}")
    print("=" * 70)

    for indice, documento in enumerate(documentos, start=1):
        metadata = documento.metadata

        print(f"\n[{indice}]")
        print(f"Documento: {metadata.get('documento')}")
        print(f"Página: {metadata.get('pagina')}")
        print(f"Tipo: {metadata.get('content_type', 'chunk_normal')}")
        print(f"ID: {metadata.get('chunk_id')}")
        print("Conteúdo:")
        print(documento.page_content)
        print("-" * 70)


if __name__ == "__main__":
    main()
