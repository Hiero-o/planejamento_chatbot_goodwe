import re
from collections.abc import Mapping, Sequence
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 80

DEFAULT_EXCLUDED_PAGES: dict[str, set[int]] = {
    "GW_HCA-G2_User-Manual-PT.pdf": {3, 4},
}


def _extract_table_contexts(
    page_text: str,
) -> list[tuple[str, int, str, str]]:
    """
    Extrai contextos especializados das tabelas técnicas GoodWe HCA-G2.

    Retorna tuplas com:
        texto, posição, tipo de contexto e sufixo do ID.
    """

    normalized_text = re.sub(r"\s+", " ", page_text).strip()

    contexts = []

    # 1. Detecta o protocolo de comunicação independentemente
    # da presença dos três nomes dos modelos na mesma página.
    protocol_pattern = re.compile(
        r"\bProtocolo\s+de\s+comunicação\s+"
        r"(Modbus\s+TCP)\b",
        re.IGNORECASE,
    )

    protocol_match = protocol_pattern.search(normalized_text)

    if protocol_match:
        context_text = (
            "GoodWe HCA-G2; "
            "protocolo de comunicação: Modbus TCP."
        )

        start_index = page_text.casefold().find(
            "protocolo de comunicação".casefold()
        )

        if start_index < 0:
            start_index = 0

        contexts.append(
            (
                context_text,
                start_index,
                "derived_table_protocol_context",
                "table_communication_protocol",
            )
        )

    # 2. As três especificações seguintes precisam dos três modelos.
    model_pattern = re.compile(
        r"\bGW(?:7K|11K|22K)-\s*HCA-20\b",
        re.IGNORECASE,
    )

    models_found = {
        re.sub(r"\s+", "", match.group(0)).upper()
        for match in model_pattern.finditer(normalized_text)
    }

    ordered_models = [
        "GW7K-HCA-20",
        "GW11K-HCA-20",
        "GW22K-HCA-20",
    ]

    if not set(ordered_models).issubset(models_found):
        return contexts

    specifications = [
        {
            "label": "Potência nominal de saída",
            "unit": "W",
            "pattern": re.compile(
                r"Potência\s+nominal\s+de\s+saída"
                r"\s*(?:\(\s*W\s*\))?"
                r"\s*(\d{4,5})\s+(\d{4,5})\s+(\d{4,5})",
                re.IGNORECASE,
            ),
            "content_type": "derived_table_power_context",
            "id_suffix": "table_power_output",
        },
        {
            "label": "Tensão nominal de saída",
            "unit": "V",
            "pattern": re.compile(
                r"Tensão\s+nominal\s+de\s+saída"
                r"\s*(?:\(\s*V\s*\))?"
                r"\s*(\d{2,3})\s+(\d{2,3})\s+(\d{2,3})",
                re.IGNORECASE,
            ),
            "content_type": "derived_table_voltage_context",
            "id_suffix": "table_output_voltage",
        },
        {
            "label": "Corrente nominal de saída",
            "unit": "A",
            "pattern": re.compile(
                r"Corrente\s+nominal\s+de\s+saída"
                r"\s*(?:\(\s*A\s*\))?"
                r"\s*(\d{1,3})\s+(\d{1,3})\s+(\d{1,3})",
                re.IGNORECASE,
            ),
            "content_type": "derived_table_current_context",
            "id_suffix": "table_output_current",
        },
    ]

    for specification in specifications:
        match = specification["pattern"].search(normalized_text)

        if match is None:
            continue

        values = [str(int(value)) for value in match.groups()]

        model_values = "; ".join(
            f"{model}={value}{specification['unit']}"
            for model, value in zip(ordered_models, values)
        )

        context_text = (
            f"GoodWe HCA-G2; {specification['label']} "
            f"({specification['unit']}): {model_values}"
        )

        start_index = page_text.casefold().find(
            specification["label"].casefold()
        )

        if start_index < 0:
            start_index = 0

        contexts.append(
            (
                context_text,
                start_index,
                specification["content_type"],
                specification["id_suffix"],
            )
        )

    return contexts


def split_pages_into_chunks(
    pages: Sequence[Mapping[str, Any]],
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    excluded_pages_by_document: Mapping[str, set[int]] | None = None,
) -> list[Document]:
    """Divide páginas em chunks e preserva os metadados de origem."""

    if chunk_size <= 0:
        raise ValueError("chunk_size deve ser maior que zero.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap não pode ser negativo.")

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap deve ser menor que chunk_size."
        )

    exclusions = (
        DEFAULT_EXCLUDED_PAGES
        if excluded_pages_by_document is None
        else excluded_pages_by_document
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
                f"O número de página deve ser positivo: {page_number}."
            )

        if page_number in exclusions.get(document_name, set()):
            continue

        base_metadata = {
            "documento": document_name,
            "source": source_path,
            "pagina": page_number,
            "page": page_number,
        }

        # 1. Chunks normais.
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

        # 2. Contextos especializados da tabela técnica.
        table_contexts = _extract_table_contexts(page_text)

        for context_text, start_index, content_type, id_suffix in (
            table_contexts
        ):
            if len(context_text) > chunk_size:
                continue

            metadata = {
                **base_metadata,
                "start_index": start_index,
                "chunk_index": len(page_chunks),
                "chunk_id": (
                    f"{document_name}|p{page_number}|{id_suffix}"
                ),
                "chunk_chars": len(context_text),
                "content_type": content_type,
            }

            chunks.append(
                Document(
                    page_content=context_text,
                    metadata=metadata,
                )
            )

    return chunks