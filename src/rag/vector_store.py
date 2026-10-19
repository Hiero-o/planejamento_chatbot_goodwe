import os
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_chroma import Chroma

from src.rag.embeddings import create_embeddings


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_PERSIST_DIRECTORY = PROJECT_ROOT / "data" / "chroma_db"
DEFAULT_COLLECTION_PREFIX = "gurai"


def _model_fragment(model_name: str) -> str:
    """
    Converte o nome do modelo em um fragmento válido
    para o nome da coleção.
    """
    fragment = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        model_name.lower(),
    ).strip("_-")

    return fragment or "default"


def create_vector_store(
    *,
    provider: str | None = None,
    persist_directory: str | Path | None = None,
    collection_name: str | None = None,
) -> tuple[Chroma, str]:
    """
    Cria ou abre uma coleção persistente no ChromaDB.

    O provedor é escolhido pelo módulo embeddings.py.
    A coleção varia conforme provedor e modelo, evitando
    misturar vetores de configurações diferentes.
    """

    embeddings, selected_provider = create_embeddings(provider)

    model_name = os.getenv(
        "RAG_EMBEDDING_MODEL",
        "nomic-embed-text",
    ).strip()

    if persist_directory is None:
        db_path = DEFAULT_PERSIST_DIRECTORY
    else:
        db_path = Path(persist_directory).expanduser()

        if not db_path.is_absolute():
            db_path = PROJECT_ROOT / db_path

    db_path = db_path.resolve()
    db_path.mkdir(parents=True, exist_ok=True)

    if collection_name is None:
        collection_name = (
            f"{DEFAULT_COLLECTION_PREFIX}_"
            f"{selected_provider}_"
            f"{_model_fragment(model_name)}"
        )

    # O índice vetorial usará distância cosseno.
    # Os metadados documentam qual configuração foi utilizada.
    collection_metadata = {
        "hnsw:space": "cosine",
        "embedding_provider": selected_provider,
        "embedding_model": model_name,
    }

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(db_path),
        collection_metadata=collection_metadata,
    )

    return vector_store, selected_provider


def _read_existing_records(
    vector_store: Chroma,
) -> dict[str, tuple[str, dict[str, Any]]]:
    """
    Lê os IDs, textos e metadados já armazenados.

    Isso permite verificar quais chunks mudaram e quais
    podem ser reutilizados sem gerar embeddings novamente.
    """

    data = vector_store.get(
        include=["documents", "metadatas"],
    )

    ids = data.get("ids") or []
    texts = data.get("documents") or []
    metadatas = data.get("metadatas") or []

    existing: dict[str, tuple[str, dict[str, Any]]] = {}

    for index, record_id in enumerate(ids):
        text = texts[index] if index < len(texts) else ""
        metadata = (
            metadatas[index]
            if index < len(metadatas) and metadatas[index]
            else {}
        )

        existing[record_id] = (text or "", dict(metadata))

    return existing


def index_chunks(
    vector_store: Chroma,
    chunks: Sequence[Document],
    *,
    batch_size: int = 64,
) -> dict[str, int]:
    """
    Sincroniza os chunks com a coleção persistente.

    - Insere chunks novos.
    - Atualiza chunks cujo texto ou metadados mudaram.
    - Preserva chunks que continuam iguais.
    - Remove chunks antigos que não fazem mais parte da base.

    Os IDs determinísticos são lidos do metadado chunk_id.
    """

    if batch_size <= 0:
        raise ValueError("batch_size deve ser maior que zero.")

    documents = list(chunks)

    if not documents:
        raise ValueError(
            "A lista de chunks está vazia. "
            "A indexação foi interrompida para evitar "
            "uma remoção acidental de toda a coleção."
        )

    ids: list[str] = []

    for document in documents:
        chunk_id = document.metadata.get("chunk_id")

        if not isinstance(chunk_id, str) or not chunk_id.strip():
            raise ValueError(
                "Todo chunk precisa de um chunk_id válido."
            )

        ids.append(chunk_id)

    if len(ids) != len(set(ids)):
        raise ValueError(
            "Foram encontrados chunk_id duplicados."
        )

    existing = _read_existing_records(vector_store)

    expected_ids = set(ids)

    # Seleciona apenas documentos novos ou alterados.
    to_upsert: list[Document] = []

    for document, chunk_id in zip(documents, ids):
        existing_record = existing.get(chunk_id)

        if existing_record is None:
            to_upsert.append(document)
            continue

        existing_text, existing_metadata = existing_record

        if (
            existing_text != document.page_content
            or existing_metadata != document.metadata
        ):
            to_upsert.append(document)

    # Inserção/atualização em lotes para controlar o volume
    # de processamento de embeddings por chamada.
    for start in range(0, len(to_upsert), batch_size):
        batch = to_upsert[start:start + batch_size]

        batch_ids = [
            str(document.metadata["chunk_id"])
            for document in batch
        ]

        vector_store.add_documents(
            documents=batch,
            ids=batch_ids,
        )

    # Remove somente registros que deixaram de existir
    # na nova lista de chunks.
    stale_ids = sorted(set(existing) - expected_ids)

    if stale_ids:
        vector_store.delete(ids=stale_ids)

    unchanged_count = len(documents) - len(to_upsert)

    return {
        "total_chunks": len(documents),
        "inseridos_ou_atualizados": len(to_upsert),
        "inalterados": unchanged_count,
        "removidos_obsoletos": len(stale_ids),
    }