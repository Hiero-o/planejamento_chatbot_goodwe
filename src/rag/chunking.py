from collections.abc import Mapping, Sequence
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_CHUNK_SIZE = 128
DEFAULT_CHUNK_OVERLAP = 24


def split_pages_into_chunks(
    pages: Sequence[Mapping[str, Any]],
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    """
    Divide páginas em chunks e preserva os metadados da origem.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size deve ser maior que zero.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap não pode ser negativo.")

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap deve ser menor que chunk_size."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
        add_start_index=True,
        strip_whitespace=True,
    )

    chunks: list[Document] = []

    for page in pages:
        page_text = page.get("texto", "")

        if not isinstance(page_text, str):
            raise TypeError(
                "O campo 'texto' de cada página deve ser uma string."
            )

        page_text = page_text.strip()

        if not page_text:
            continue

        document_name = str(
            page.get("documento") or "documento_desconhecido"
        )

        # IMPORTANTE:
        # Recupera o VALOR do caminho, não o nome da chave.
        source_path = page.get("caminho")

        if not isinstance(source_path, str) or not source_path.strip():
            source_path = document_name
        else:
            source_path = source_path.strip()

        try:
            page_number = int(page.get("pagina", 1))
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Número de página inválido para {document_name}."
            ) from error

        if page_number < 1:
            raise ValueError(
                f"O número da página deve ser positivo: {page_number}."
            )

        base_metadata = {
            "documento": document_name,
            "source": source_path,
            "pagina": page_number,
            "page": page_number,
        }

        page_chunks = splitter.create_documents(
            texts=[page_text],
            metadatas=[base_metadata],
        )

        for chunk_index, split_document in enumerate(page_chunks):
            metadata = dict(split_document.metadata)

            metadata["chunk_index"] = chunk_index
            metadata["chunk_id"] = (
                f"{document_name}|p{page_number}|c{chunk_index:04d}"
            )
            metadata["chunk_chars"] = len(
                split_document.page_content
            )

            chunks.append(
                Document(
                    page_content=split_document.page_content,
                    metadata=metadata,
                )
            )

    return chunks