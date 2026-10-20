from services.rag.document_loader import load_documents
from src.rag.chunking import split_pages_into_chunks
from src.rag.vector_store import (
    DEFAULT_PERSIST_DIRECTORY,
    create_vector_store,
    index_chunks,
)


def main() -> None:
    print("=" * 60)
    print("INDEXAÇÃO COMPLETA — GURAI SPRINT 04")
    print("=" * 60)

    pages = load_documents()

    if not pages:
        raise AssertionError(
            "Nenhuma página foi carregada. "
            "A indexação foi interrompida."
        )

    print(f"Páginas carregadas: {len(pages)}")

    # Configuração escolhida após os testes experimentais.
    chunks = split_pages_into_chunks(
        pages,
        chunk_size=512,
        chunk_overlap=80,
    )

    if not chunks:
        raise AssertionError(
            "Nenhum chunk foi gerado. "
            "A indexação foi interrompida."
        )

    derived_chunks = [
        chunk
        for chunk in chunks
        if str(
            chunk.metadata.get("content_type", "")
        ).startswith("derived_table_")
    ]

    print(f"Chunks gerados: {len(chunks)}")
    print(f"Contextos técnicos especiais: {len(derived_chunks)}")

    vector_store, provider = create_vector_store(
        provider="local",
    )

    print(f"Provedor de embeddings: {provider}")
    print(
        "Diretório do ChromaDB:",
        DEFAULT_PERSIST_DIRECTORY,
    )

    # Sincroniza a coleção definitiva com a configuração escolhida.
    stats = index_chunks(vector_store, chunks)

    print("\nResultado da indexação:")

    for field, value in stats.items():
        print(f"{field}: {value}")

    # Confirma que a coleção contém exatamente os IDs esperados.
    stored_data = vector_store.get(
        include=["metadatas"],
    )

    stored_ids = set(stored_data.get("ids") or [])

    expected_ids = {
        str(chunk.metadata["chunk_id"])
        for chunk in chunks
    }

    if stored_ids != expected_ids:
        missing_ids = expected_ids - stored_ids
        unexpected_ids = stored_ids - expected_ids

        raise AssertionError(
            "A coleção persistida não corresponde à base esperada.\n"
            f"IDs ausentes: {len(missing_ids)}\n"
            f"IDs inesperados: {len(unexpected_ids)}"
        )

    print(f"\nIDs persistidos: {len(stored_ids)}")
    print("[OK] Todos os chunks estão persistidos.")
    print("[OK] Não existem IDs extras na coleção.")

    print("\n" + "=" * 60)
    print("INDEXAÇÃO VALIDADA COM SUCESSO")
    print("=" * 60)


if __name__ == "__main__":
    main()