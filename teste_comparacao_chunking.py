import re
import unicodedata
from pathlib import Path

from services.rag.document_loader import load_documents
from src.rag.chunking import split_pages_into_chunks
from src.rag.retriever import GurAIHybridRetriever
from src.rag.vector_store import create_vector_store, index_chunks


PROJECT_ROOT = Path(__file__).resolve().parent
TEST_DB_PATH = PROJECT_ROOT / "data" / "chroma_test"

TOP_K = 4
CANDIDATE_K = 24

CONFIGURATIONS = [
    {
        "name": "128/24",
        "chunk_size": 128,
        "chunk_overlap": 24,
        "collection_name": "gurai_compare_chunk128_overlap24",
    },
    {
        "name": "512/80",
        "chunk_size": 512,
        "chunk_overlap": 80,
        "collection_name": "gurai_compare_chunk512_overlap80",
    },
]

TEST_CASES = [
    {
        "id": "potencia_7k",
        "question": "Qual é a potência nominal do modelo GW7K-HCA-20?",
        "expected_all": ["GW7K-HCA-20=7000"],
        "expected_any": [],
    },
    {
        "id": "potencia_11k",
        "question": "Qual é a potência nominal do modelo GW11K-HCA-20?",
        "expected_all": ["GW11K-HCA-20=11000"],
        "expected_any": [],
    },
    {
        "id": "potencia_22k",
        "question": "Qual é a potência nominal do modelo GW22K-HCA-20?",
        "expected_all": ["GW22K-HCA-20=22000"],
        "expected_any": [],
    },
    {
        "id": "tensao_saida",
        "question": "Qual é a tensão nominal de saída dos carregadores?",
        "expected_all": [],
        "expected_any": ["tensão nominal de saída"],
    },
    {
        "id": "corrente_saida",
        "question": "Qual é a corrente nominal de saída dos carregadores?",
        "expected_all": [],
        "expected_any": ["corrente nominal de saída"],
    },
    {
        "id": "seguranca",
        "question": (
            "Quais cuidados de segurança devem ser tomados "
            "antes de qualquer operação no carregador?"
        ),
        "expected_all": [],
        "expected_any": [
            "use EPI",
            "carregador esteja desligado",
            "desconecte o carregador",
        ],
    },
    {
        "id": "orientacao",
        "question": (
            "Como o carregador deve ser posicionado durante "
            "a instalação?"
        ),
        "expected_all": [],
        "expected_any": ["verticalmente", "horizontalmente"],
    },
    {
        "id": "modbus_funcao",
        "question": (
            "Qual é a função do registro MODBUS 10000, "
            "EMS Energy Dispatch?"
        ),
        "expected_all": [],
        "expected_any": [
            "adjust the charging station's power to the minimum for charging",
            "normal operation",
        ],
    },
    {
        "id": "modbus_tipo",
        "question": (
            "Qual é o tipo de dado e o modo de acesso "
            "do registro MODBUS 10000?"
        ),
        "expected_all": ["u16", "rw"],
        "expected_any": [],
    },
    {
        "id": "protocolo",
        "question": "Qual protocolo de comunicação o carregador utiliza?",
        "expected_all": [],
        "expected_any": ["modbus tcp"],
    },
]


def normalize_text(text: str) -> str:
    """Normaliza acentos, maiúsculas e espaços para a avaliação."""
    text = unicodedata.normalize("NFKD", text.casefold())

    text = "".join(
        char
        for char in text
        if not unicodedata.combining(char)
    )

    return re.sub(r"\s+", " ", text).strip()


def evaluate_retrieval(test_case, documents) -> tuple[bool, list[str]]:
    """
    Verifica se os resultados recuperados contêm os sinais esperados.

    expected_all: todos os termos devem estar presentes.
    expected_any: pelo menos um dos termos deve estar presente.
    """
    combined_text = normalize_text(
        "\n".join(document.page_content for document in documents)
    )

    expected_all = test_case["expected_all"]
    expected_any = test_case["expected_any"]

    missing_terms = [
        term
        for term in expected_all
        if normalize_text(term) not in combined_text
    ]

    all_conditions_met = not missing_terms

    any_condition_met = (
        not expected_any
        or any(
            normalize_text(term) in combined_text
            for term in expected_any
        )
    )

    hit = all_conditions_met and any_condition_met

    return hit, missing_terms


def create_experimental_collection(pages, configuration):
    """Gera, indexa e valida uma coleção experimental isolada."""

    name = configuration["name"]
    chunk_size = configuration["chunk_size"]
    chunk_overlap = configuration["chunk_overlap"]

    print("\n" + "=" * 75)
    print(f"PREPARANDO CONFIGURAÇÃO {name}")
    print("=" * 75)

    chunks = split_pages_into_chunks(
        pages,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    if not chunks:
        raise AssertionError(
            f"Nenhum chunk gerado na configuração {name}."
        )

    derived_chunks = [
    chunk
    for chunk in chunks
    if str(
        chunk.metadata.get("content_type", "")
    ).startswith("derived_table_")
]

    print(f"Chunk size: {chunk_size}")
    print(f"Overlap: {chunk_overlap}")
    print(f"Total de chunks: {len(chunks)}")
    print(f"Contextos especiais: {len(derived_chunks)}")

    vector_store, provider = create_vector_store(
        provider="local",
        persist_directory=TEST_DB_PATH,
        collection_name=configuration["collection_name"],
    )

    print(f"Provedor de embeddings: {provider}")
    print(f"Coleção: {configuration['collection_name']}")

    stats = index_chunks(vector_store, chunks)

    for field, value in stats.items():
        print(f"{field}: {value}")

    stored_data = vector_store.get(include=["metadatas"])
    stored_ids = set(stored_data.get("ids") or [])

    expected_ids = {
        str(chunk.metadata["chunk_id"])
        for chunk in chunks
    }

    if stored_ids != expected_ids:
        raise AssertionError(
            f"A coleção {name} não corresponde aos chunks atuais.\n"
            f"IDs ausentes: {len(expected_ids - stored_ids)}\n"
            f"IDs inesperados: {len(stored_ids - expected_ids)}"
        )

    print(f"[OK] {len(stored_ids)} chunks persistidos e validados.")

    retriever = GurAIHybridRetriever(
        vector_store,
        k=TOP_K,
        candidate_k=CANDIDATE_K,
    )

    return {
        "name": name,
        "chunk_count": len(chunks),
        "retriever": retriever,
    }


def evaluate_configuration(configuration):
    """Executa as 10 perguntas e registra os resultados Hit@4."""

    name = configuration["name"]
    retriever = configuration["retriever"]
    hits = {}

    print("\n" + "#" * 75)
    print(f"AVALIAÇÃO — CONFIGURAÇÃO {name}")
    print("#" * 75)

    for test_case in TEST_CASES:
        question = test_case["question"]
        results = retriever.invoke(question)

        hit, missing_terms = evaluate_retrieval(
            test_case,
            results,
        )

        hits[test_case["id"]] = hit

        status = "HIT@4" if hit else "MISS@4"

        print(f"\n[{status}] {test_case['id']}")
        print(f"Pergunta: {question}")

        if test_case["expected_all"]:
            print(
                "Termos obrigatórios: "
                + ", ".join(test_case["expected_all"])
            )

        if test_case["expected_any"]:
            print(
                "Sinais esperados (qualquer um): "
                + " | ".join(test_case["expected_any"])
            )

        if missing_terms:
            print("Termos obrigatórios ausentes: " + ", ".join(missing_terms))

        if not results:
            print("Nenhum resultado encontrado.")
            continue

        for rank, document in enumerate(results, start=1):
            metadata = document.metadata

            snippet = re.sub(
                r"\s+",
                " ",
                document.page_content,
            ).strip()

            if len(snippet) > 180:
                snippet = snippet[:180] + "..."

            print(
                f"  {rank}. "
                f"{metadata.get('documento')} | "
                f"p. {metadata.get('pagina')} | "
                f"{metadata.get('content_type', 'normal')}"
            )
            print(f"     {snippet}")

    total_hits = sum(hits.values())
    total_questions = len(TEST_CASES)

    print(
        f"\nRESUMO {name}: "
        f"{total_hits}/{total_questions} sinais recuperados "
        f"({total_hits / total_questions:.0%})"
    )

    return hits


def main():
    print("=" * 75)
    print("AVALIAÇÃO DO RETRIEVER — GURAI SPRINT 04")
    print("=" * 75)
    print(f"Banco experimental: {TEST_DB_PATH}")
    print(f"Perguntas: {len(TEST_CASES)}")
    print(f"Top K: {TOP_K}")
    print(f"Candidate K: {CANDIDATE_K}")

    pages = load_documents()

    if not pages:
        raise AssertionError("Nenhuma página foi carregada.")

    print(f"Páginas carregadas: {len(pages)}")

    experiments = []

    for configuration in CONFIGURATIONS:
        experiment = create_experimental_collection(
            pages,
            configuration,
        )
        experiments.append(experiment)

    results_by_name = {}

    for experiment in experiments:
        hits = evaluate_configuration(experiment)
        results_by_name[experiment["name"]] = hits

    # Compara o resultado de cada pergunta entre as configurações.
    print("\n" + "=" * 75)
    print("COMPARAÇÃO FINAL — HIT@4")
    print("=" * 75)

    hits_128 = results_by_name["128/24"]
    hits_512 = results_by_name["512/80"]

    for test_case in TEST_CASES:
        case_id = test_case["id"]
        hit_128 = hits_128[case_id]
        hit_512 = hits_512[case_id]

        if hit_128 and hit_512:
            comparison = "AMBAS"
        elif hit_128:
            comparison = "128/24"
        elif hit_512:
            comparison = "512/80"
        else:
            comparison = "NENHUMA"

        print(f"{case_id}: {comparison}")

    total = len(TEST_CASES)
    total_128 = sum(hits_128.values())
    total_512 = sum(hits_512.values())

    print("\n" + "-" * 75)
    print(f"128/24: {total_128}/{total} ({total_128 / total:.0%})")
    print(f"512/80: {total_512}/{total} ({total_512 / total:.0%})")
    print("-" * 75)

    print(
        "\nObservação: Hit@4 verifica sinais textuais esperados "
        "nos quatro primeiros resultados. Não mede, sozinho, "
        "a correção completa de uma resposta gerada."
    )

    print("\n[OK] Avaliação concluída.")
    print("[OK] A coleção Chroma definitiva não foi modificada.")


if __name__ == "__main__":
    main()