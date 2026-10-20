from functools import lru_cache
from collections.abc import Sequence

from langchain_core.documents import Document

from src.rag.retriever import(
    GurAIHybridRetriever,
    create_retriever,
)



DEFAULT_TOP_K = 4
DEFAULT_CANDIDATE_K = 24

@lru_cache(maxsize=1)
def get_documentation_retriever() -> GurAIHybridRetriever:
    # Inicia Retriever uma vez por processo, usa chroma db principal e embeddings locais configurados no projeto.
    
    retriever, provider = create_retriever(
        provider="local",
        k=DEFAULT_TOP_K,
        candidate_k=DEFAULT_CANDIDATE_K,
    )
    print(
        "[RAG] Retriever documental inicializado. "
        f"Provedor de embeddings: {provider}"
    )

    return retriever


def format_documentation_context(
    documents: Sequence[Document],
) -> str:
    #formata docs recuperados para o prompt do llm, cada techo conserva nome do doc, pagina de origem, permitindo que a resposta cite fontes verificáveis.
    
    sections = []
    
    for index, document in enumerate(documents, start=1):
        content = document.page_content.strip()
        if not content:
            continue
        
        metadata = document.metadata or {}
        
        document_name = metadata.get("documento")
        source_path = metadata.get("source")
        
        if not document_name and source_path:
            document_name = (
                str(source_path).replace("\\", "/").rsplit("/", maxsplit=1)[-1]
            )
            
            
        if not document_name:
            document_name = "Documento não identificado"

        page_number = metadata.get("pagina")

        if page_number is None:
            page_number = metadata.get("page")

        if page_number is None:
            page_number = "não identificada"
            
        
        sections.append("\n".join(
                [
                    f"[Trecho {index}]",
                    f"Documento: {document_name}",
                    f"Página: {page_number}",
                    "Conteúdo:",
                    content,
                ]
            )
        )
    return "\n\n---\n\n".join(sections)
    
    
def build_documentation_context(question: str) -> str | None:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("A pergunta não pode estar vazia.")
    
    
    retriever = get_documentation_retriever()
    documents = retriever.invoke(question)
    
    if not documents:
        return None
    
    context = format_documentation_context(documents)
    
    if not context.strip():
        return None
    return context