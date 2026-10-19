import os
import warnings

from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings

CLOUID_BASE_URL = "https://ollama.com"
DEFAULT_LOCAL_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL_NAME = "nomic-embed-text"

PROBE_TEXT = "teste de geração de embeddings do GurAI"



def _create_and_validate(
    provider: str,
    model_name: str,
    local_base_url: str,
) -> tuple[Embeddings, int]:
    
    if provider == "cloud":
        base_url = CLOUID_BASE_URL
    elif provider == "local":
        base_url = local_base_url
    else:
        raise ValueError(f"Provedor deconhecido: {provider}.")
    
    embeddings = OllamaEmbeddings(
        model=model_name,
        base_url=base_url,
    )
    
    vetor = embeddings.embed_query(PROBE_TEXT)
    
    if not vetor:
        raise RuntimeError(f"O provedor {provider} retornou um vetor vazio")
    if not all(isinstance(value, (int, float)) for value in vetor):
        raise RuntimeError(f"O provedor {provider} retornou valores inválidos.")
    return embeddings, len(vetor)


def create_embeddings(provider: str | None = None,) -> tuple[Embeddings, str]:
    load_dotenv()
    selected_provider = (provider or os.getenv("RAG_EMBEDDING_PROVIDER", "auto")).strip().lower()
    
    model_name = os.getenv("RAG_EMBEDDING_MODEL", DEFAULT_MODEL_NAME,).strip()
    
    local_base_url = os.getenv("OLLAMA_LOCAL_BASE_URL", DEFAULT_LOCAL_BASE_URL,).strip()
    if not model_name:
        raise ValueError("RAG_EMBEDDING_MODEL não pode estar vazio.")
    
    if selected_provider not in {"local", "cloud", "auto"}:
        raise ValueError("RAG_EMBEDDING_PROVIDER deve ser ", "'local', 'cloud', ou 'auto'.")
    
    
    if selected_provider == "local":
        embeddings, dimension = _create_and_validate("local", model_name, local_base_url,)
        print(f"Embeddings selecionados: local | " f"modelo={model_name} | dimensão={dimension}")
        
        return embeddings, "local"

    if selected_provider == "cloud":
        if not os.getenv("OLLAMA_API_KEY"):
            raise RuntimeError("OLLAMA_API_KEY não está configurada. configure a chave antes de tentar usar o Cloud")
        
        try:
            embeddings, dimension = _create_and_validate("cloud", model_name, local_base_url,)
        
        except Exception as error:
            raise RuntimeError(
                "não foi possível inicializar os embeddings "
                f"No Ollama Cloud ({type(error).__name__})."
            ) from error
        print(f"Embeddings selecionados: cloud | " f"modelo={model_name} | dimensão{dimension}")
        
        return embeddings, "cloud"
    
    if os.getenv("OLLAMA_API_KEY"):
        try:
            embeddings, dimension = _create_and_validate("cloud", model_name,local_base_url,)
            print(f"Embeddings selecionados: cloud | " f"modelo={model_name} | dimensao={dimension}")
            return embeddings, "cloud"

        except Exception as error:
            warnings.warn(
                "Ollama Cloud indisponível para embeddings "
                f"({type(error).__name__}); recorrendo ao "
                "Ollama local.",
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

        # Fallback: inicializa e valida o Ollama local.
        try:
            embeddings, dimension = _create_and_validate(
                "local",
                model_name,
                local_base_url,
            )
        except Exception as error:
            raise RuntimeError(
                "Não foi possível gerar embeddings nem pelo Cloud "
                "nem pelo Ollama local. Verifique o servidor, "
                "o modelo e a configuração."
            ) from error

        print(
            f"Embeddings selecionados: local | "
            f"modelo={model_name} | dimensão={dimension}"
        )

        return embeddings, "local"
            