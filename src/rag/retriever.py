import re
import unicodedata
from collections import Counter
from math import log
from pathlib import Path

from langchain_core.documents import Document

from src.rag.vector_store import create_vector_store


DEFAULT_TOP_K = 4
DEFAULT_CANDIDATE_K = 24
RRF_CONSTANT = 60

STOPWORDS = {
    "a", "o", "os", "as",
    "de", "do", "da", "dos", "das",
    "um", "uma", "uns", "umas",
    "e", "ou", "em", "no", "na", "nos", "nas",
    "qual", "quais", "que", "como", "quando",
    "onde", "por", "para", "com", "sem",
    "é", "são", "ser", "foi", "será",
    "me", "se", "ao", "aos", "à", "às",
}

POWER_QUERY_TERMS = {
    "potencia", "potencias", "power", "powers",
    "watt", "watts", "kw",
}

VOLTAGE_QUERY_TERMS = {
    "tensao", "voltage", "volt", "volts",
}

CURRENT_QUERY_TERMS = {
    "corrente", "current", "ampere", "amperes",
    "amp", "amps",
}

PROTOCOL_QUERY_TERMS = {
    "protocolo",
    "protocol",
    "comunicacao",
    "communication",
}


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.casefold())

    return "".join(
        char
        for char in normalized
        if not unicodedata.combining(char)
    )


def _tokenize(text: str) -> list[str]:
    normalized = _normalize_text(text)
    tokens = re.findall(r"[a-z0-9]+", normalized)

    return [
        token
        for token in tokens
        if token not in STOPWORDS
    ]


def _find_numeric_identifiers(text: str) -> list[str]:
    """Localiza endereços numéricos e códigos de exceção MODBUS em hexadecimal."""
    return re.findall(
        r"\b0x[0-9a-f]{4}\b|(?<!\d)\d{5,6}(?!\d)",
        text,
        flags=re.IGNORECASE,
    )


class GurAIHybridRetriever:
    """
    Busca híbrida com prioridade para identificadores MODBUS
    e contextos especializados de potência, tensão e corrente.
    """

    def __init__(
        self,
        vector_store,
        *,
        k: int = DEFAULT_TOP_K,
        candidate_k: int = DEFAULT_CANDIDATE_K,
    ) -> None:
        if k < 1:
            raise ValueError("k deve ser maior ou igual a 1.")

        if candidate_k < 1:
            raise ValueError(
                "candidate_k deve ser maior ou igual a 1."
            )

        self.vector_store = vector_store
        self.k = k
        self.candidate_k = candidate_k

        stored = vector_store.get(
            include=["documents", "metadatas"],
        )

        ids = stored.get("ids") or []
        texts = stored.get("documents") or []
        metadatas = stored.get("metadatas") or []

        self.documents: dict[str, Document] = {}

        for index, record_id in enumerate(ids):
            if index >= len(texts) or texts[index] is None:
                continue

            metadata = (
                metadatas[index]
                if index < len(metadatas) and metadatas[index]
                else {}
            )

            self.documents[record_id] = Document(
                page_content=texts[index],
                metadata=dict(metadata),
            )

        self.tokens_by_id = {
            record_id: set(_tokenize(document.page_content))
            for record_id, document in self.documents.items()
        }

        self.idf = self._calculate_idf()

    def _calculate_idf(self) -> dict[str, float]:
        total_documents = len(self.tokens_by_id)

        if total_documents == 0:
            return {}

        document_frequency: Counter[str] = Counter()

        for tokens in self.tokens_by_id.values():
            document_frequency.update(tokens)

        return {
            token: log(
                1
                + (
                    total_documents - frequency + 0.5
                ) / (
                    frequency + 0.5
                )
            )
            for token, frequency in document_frequency.items()
        }

    def _lexical_score(
        self,
        query_tokens: set[str],
        document_tokens: set[str],
    ) -> float:
        matched_terms = query_tokens & document_tokens

        return sum(
            self.idf.get(term, 0.0)
            for term in matched_terms
        )
        
    
    def _is_relevant_charging_limit_context(
        self,
        record_id: str,
        query_tokens: set[str],
    ) -> bool:
        """Prioriza trechos sobre potência máxima e limitação pelo OBC."""

        asks_about_charging_limit = (
            {"potencia", "maxima", "carregamento"}.issubset(
                query_tokens
            )
            or {"obc", "potencia"}.issubset(query_tokens)
        )

        if not asks_about_charging_limit:
            return False

        document_tokens = set(
            _tokenize(
                self.documents[record_id].page_content
            )
        )

        return (
            "obc" in document_tokens
            and "potencia" in document_tokens
            and "carregamento" in document_tokens
            and bool({"maxima", "real"} & document_tokens)
        )


    def _is_relevant_table_context(
    self,
    record_id: str,
    query_tokens: set[str],
    ) -> bool:
        """Prioriza o contexto técnico correspondente à pergunta."""

        content_type = self.documents[record_id].metadata.get(
            "content_type"
        )

        if (
            content_type == "derived_table_power_context"
            and query_tokens & POWER_QUERY_TERMS
        ):
            return True

        if (
            content_type == "derived_table_voltage_context"
            and query_tokens & VOLTAGE_QUERY_TERMS
        ):
            return True

        if (
            content_type == "derived_table_current_context"
            and query_tokens & CURRENT_QUERY_TERMS
        ):
            return True

        if (
            content_type == "derived_table_protocol_context"
            and query_tokens & PROTOCOL_QUERY_TERMS
        ):
            return True

        # Prioriza o contexto que reconstrói as linhas da tabela
        # Modbus Exception Codes quando a pergunta contém um código hexadecimal.
        if content_type == "derived_table_modbus_exception_codes":
            query_text = " ".join(query_tokens)
            return re.search(
                r"\b0x[0-9a-f]{4}\b",
                query_text,
                flags=re.IGNORECASE,
            ) is not None

        return False

    def invoke(self, query: str) -> list[Document]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("A pergunta não pode estar vazia.")

        query_tokens = set(_tokenize(query))

        semantic_results = self.vector_store.similarity_search(
            query,
            k=min(self.candidate_k, len(self.documents)),
        )

        semantic_rank: dict[str, int] = {}

        for rank, document in enumerate(semantic_results, start=1):
            chunk_id = document.metadata.get("chunk_id")

            if chunk_id in self.documents:
                semantic_rank[chunk_id] = rank

        lexical_scores = {
            record_id: self._lexical_score(
                query_tokens,
                self.tokens_by_id[record_id],
            )
            for record_id in self.documents
        }

        lexical_results = sorted(
            (
                record_id
                for record_id, score in lexical_scores.items()
                if score > 0
            ),
            key=lambda record_id: (
                -lexical_scores[record_id],
                record_id,
            ),
        )

        lexical_rank = {
            record_id: rank
            for rank, record_id in enumerate(
                lexical_results,
                start=1,
            )
        }

        candidate_ids = set(semantic_rank) | set(lexical_rank)

        requested_identifiers = set(
            _find_numeric_identifiers(query)
        )

        exact_identifier_ids = set()

        for record_id, document in self.documents.items():
            document_identifiers = set(
                _find_numeric_identifiers(
                    document.page_content
                )
            )

            if requested_identifiers & document_identifiers:
                exact_identifier_ids.add(record_id)

        candidate_ids |= exact_identifier_ids

        def fused_score(record_id: str) -> float:
            score = 0.0

            if record_id in semantic_rank:
                score += 1 / (
                    RRF_CONSTANT + semantic_rank[record_id]
                )

            if record_id in lexical_rank:
                score += 1 / (
                    RRF_CONSTANT + lexical_rank[record_id]
                )

            return score

        
        ordered_ids = sorted(
            candidate_ids,
            key=lambda record_id: (
                not self._is_relevant_charging_limit_context(
                    record_id,
                    query_tokens,
                ),
                record_id not in exact_identifier_ids,
                not self._is_relevant_table_context(
                    record_id,
                    query_tokens,
                ),
                -fused_score(record_id),
                -lexical_scores.get(record_id, 0.0),
                semantic_rank.get(
                    record_id,
                    float("inf"),
                ),
                record_id,
            ),
        )


        return [
            self.documents[record_id]
            for record_id in ordered_ids[:self.k]
        ]


def create_retriever(
    *,
    provider: str | None = None,
    k: int = DEFAULT_TOP_K,
    candidate_k: int = DEFAULT_CANDIDATE_K,
    persist_directory: str | Path | None = None,
    collection_name: str | None = None,
) -> tuple[GurAIHybridRetriever, str]:
    vector_store, selected_provider = create_vector_store(
        provider=provider,
        persist_directory=persist_directory,
        collection_name=collection_name,
    )

    retriever = GurAIHybridRetriever(
        vector_store,
        k=k,
        candidate_k=candidate_k,
    )

    return retriever, selected_provider