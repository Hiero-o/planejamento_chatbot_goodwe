import os
import warnings

from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings


CLOUD_BASE_URL = "https://ollama.com"
DEFAULT_LOCAL_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL_NAME = "nomic-embed-text"

PROBE_TEXT = "Teste de geração de embeddings do GurAI."


class NomicTaskPrefixEmbeddings(Embeddings):
    """
    Adiciona os prefixos recomendados pelo Nomic para busca.

    Documentos recebem 'search_document:'.
    Perguntas recebem 'search_query:'.
    """

    def __init__(self, underlying: Embeddings) -> None:
        self._underlying = underlying

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        prefixed_texts = [
            f"search_document: {text}"
            for text in texts
        ]

        return self._underlying.embed_documents(prefixed_texts)

    def embed_query(self, text: str) -> list[float]:
        prefixed_text = f"search_query: {text}"

        return self._underlying.embed_query(prefixed_text)


def _uses_nomic_prefixes(model_name: str) -> bool:
    """Verifica se o modelo utiliza os prefixos do Nomic."""
    base_name = model_name.lower().split(":")[0]

    return base_name in {
        "nomic-embed-text",
        "nomic-embed-text-v2-moe",
    }


def _create_and_validate(
    provider: str,
    model_name: str,
    local_base_url: str,
) -> tuple[Embeddings, int]:
    """
    Cria o cliente, aplica a estratégia de embeddings
    adequada ao modelo e valida a geração de um vetor.
    """

    if provider == "cloud":
        base_url = CLOUD_BASE_URL
    elif provider == "local":
        base_url = local_base_url
    else:
        raise ValueError(f"Provedor desconhecido: {provider}")

    underlying = OllamaEmbeddings(
        model=model_name,
        base_url=base_url,
    )

    if _uses_nomic_prefixes(model_name):
        embeddings: Embeddings = NomicTaskPrefixEmbeddings(
            underlying
        )
    else:
        embeddings = underlying

    vector = embeddings.embed_query(PROBE_TEXT)

    if not vector:
        raise RuntimeError(
            f"O provedor {provider} retornou um vetor vazio."
        )

    if not all(
        isinstance(value, (int, float))
        for value in vector
    ):
        raise RuntimeError(
            f"O provedor {provider} retornou valores inválidos."
        )

    return embeddings, len(vector)


def create_embeddings(
    provider: str | None = None,
) -> tuple[Embeddings, str]:
    """
    Inicializa os embeddings do GurAI.

    Opções:
        local: utiliza diretamente o Ollama local.
        cloud: tenta o endpoint Cloud, sem fallback.
        auto: tenta Cloud e recorre ao local em caso de erro.

    Retorna:
        Uma tupla contendo (embeddings, provedor selecionado).
    """

    load_dotenv()

    selected_provider = (
        provider
        or os.getenv("RAG_EMBEDDING_PROVIDER", "auto")
    ).strip().lower()

    model_name = os.getenv(
        "RAG_EMBEDDING_MODEL",
        DEFAULT_MODEL_NAME,
    ).strip()

    local_base_url = os.getenv(
        "OLLAMA_LOCAL_BASE_URL",
        DEFAULT_LOCAL_BASE_URL,
    ).strip()

    if not model_name:
        raise ValueError(
            "RAG_EMBEDDING_MODEL não pode estar vazio."
        )

    if selected_provider not in {"local", "cloud", "auto"}:
        raise ValueError(
            "RAG_EMBEDDING_PROVIDER deve ser "
            "'local', 'cloud' ou 'auto'."
        )

    if selected_provider == "local":
        embeddings, dimension = _create_and_validate(
            "local",
            model_name,
            local_base_url,
        )

        print(
            f"Embeddings selecionados: local | "
            f"modelo={model_name} | dimensão={dimension}"
        )

        return embeddings, "local"

    if selected_provider == "cloud":
        if not os.getenv("OLLAMA_API_KEY"):
            raise RuntimeError(
                "OLLAMA_API_KEY não está configurada."
            )

        try:
            embeddings, dimension = _create_and_validate(
                "cloud",
                model_name,
                local_base_url,
            )
        except Exception as error:
            raise RuntimeError(
                "Não foi possível inicializar os embeddings "
                f"no Ollama Cloud ({type(error).__name__})."
            ) from error

        print(
            f"Embeddings selecionados: cloud | "
            f"modelo={model_name} | dimensão={dimension}"
        )

        return embeddings, "cloud"

    # Modo automático.
    if os.getenv("OLLAMA_API_KEY"):
        try:
            embeddings, dimension = _create_and_validate(
                "cloud",
                model_name,
                local_base_url,
            )

            print(
                f"Embeddings selecionados: cloud | "
                f"modelo={model_name} | dimensão={dimension}"
            )

            return embeddings, "cloud"

        except Exception as error:
            warnings.warn(
                "Ollama Cloud indisponível para embeddings "
                f"({type(error).__name__}); recorrendo ao local.",
                RuntimeWarning,
                stacklevel=2,
            )
    else:
        warnings.warn(
            "OLLAMA_API_KEY não configurada; utilizando "
            "o Ollama local no modo automático.",
            RuntimeWarning,
            stacklevel=2,
        )

    try:
        embeddings, dimension = _create_and_validate(
            "local",
            model_name,
            local_base_url,
        )
    except Exception as error:
        raise RuntimeError(
            "Não foi possível gerar embeddings nem pelo Cloud "
            "nem pelo Ollama local. Verifique o servidor e o modelo."
        ) from error

    print(
        f"Embeddings selecionados: local | "
        f"modelo={model_name} | dimensão={dimension}"
    )

    return embeddings, "local"