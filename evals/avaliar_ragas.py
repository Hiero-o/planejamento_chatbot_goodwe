
import argparse
import json
import math
import re
from importlib.metadata import version
from pathlib import Path
from statistics import mean

from langchain_ollama import ChatOllama, OllamaEmbeddings
from ragas import EvaluationDataset, evaluate
from ragas.dataset_schema import SingleTurnSample
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness, ResponseRelevancy
from ragas.run_config import RunConfig


RAIZ = Path(__file__).resolve().parents[1]
PASTA_RESULTADOS = RAIZ / "evals" / "resultados"

ARQUIVOS_ENTRADA = {
    "v2": PASTA_RESULTADOS / "prompt_v2_retriever_corrigido.json",
    "v3": PASTA_RESULTADOS / "prompt_v3_retriever_corrigido.json",
}

OLLAMA_BASE_URL = "http://localhost:11434"
MODELO_AVALIADOR = "llama3:latest"
MODELO_EMBEDDINGS = "nomic-embed-text:latest"

# Referências no formato [Fonte: arquivo.pdf, p. 2]
PADRAO_BLOCO_FONTE = re.compile(
    r"\[Fonte[s]?:\s*([^\]]+)\]",
    re.IGNORECASE,
)

PADRAO_CITACAO = re.compile(
    r"(?P<documento>[^;\n]*?\.pdf)"
    r"\s*,?\s*p(?:ágina)?\.?\s*"
    r"(?P<pagina>\d+)",
    re.IGNORECASE,
)

PADRAO_DOCUMENTO = re.compile(
    r"Documento:\s*(.+?\.pdf)",
    re.IGNORECASE,
)

PADRAO_PAGINA = re.compile(
    r"Página:\s*(\d+)",
    re.IGNORECASE,
)


def separar_contextos(texto):
    """Divide os contextos recuperados em trechos individuais."""

    if not isinstance(texto, str) or not texto.strip():
        return []

    trechos = re.split(r"\n\s*---\s*\n", texto.strip())

    return [
        trecho.strip()
        for trecho in trechos
        if trecho.strip()
    ]


def normalizar_documento(documento):
    """Padroniza o nome de um PDF para comparação."""

    return documento.strip().strip("`'\"").lower()


def extrair_citacoes(resposta):
    """Extrai os pares documento/página citados na resposta."""

    citacoes = []

    for bloco in PADRAO_BLOCO_FONTE.findall(resposta or ""):
        for parte in bloco.split(";"):
            correspondencia = PADRAO_CITACAO.search(parte.strip())

            if not correspondencia:
                continue

            documento = normalizar_documento(
                correspondencia.group("documento")
            )
            pagina = int(correspondencia.group("pagina"))

            citacoes.append({
                "documento": documento,
                "pagina": pagina,
            })

    return citacoes


def remover_citacoes(resposta):
    """Retira referências documentais do texto avaliado pelo RAGAS."""

    texto = PADRAO_BLOCO_FONTE.sub("", resposta or "")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()


def extrair_fontes_contexto(contextos):
    """Obtém os pares documento/página presentes nos contextos."""

    fontes = set()

    for contexto in contextos:
        documento = PADRAO_DOCUMENTO.search(contexto)
        pagina = PADRAO_PAGINA.search(contexto)

        if documento and pagina:
            fontes.add((
                normalizar_documento(documento.group(1)),
                int(pagina.group(1)),
            ))

    return fontes


def avaliar_citacoes(resposta_original, contextos):
    """
    Verifica se cada referência citada aparece nos contextos.

    A checagem é determinística: não usa o LLM avaliador.
    Ela verifica a presença da fonte, não se todo o conteúdo
    da resposta está comprovado pela fonte.
    """

    citacoes = extrair_citacoes(resposta_original)
    fontes_contexto = extrair_fontes_contexto(contextos)

    validas = [
        citacao
        for citacao in citacoes
        if (
            citacao["documento"],
            citacao["pagina"],
        ) in fontes_contexto
    ]

    if citacoes:
        precisao = len(validas) / len(citacoes)
    else:
        # O caso sem citações precisa ser interpretado com cuidado.
        precisao = 0.0

    return {
        "quantidade_citacoes": len(citacoes),
        "quantidade_citacoes_presentes_no_contexto": len(validas),
        "precisao_referencias": precisao,
        "citacoes": citacoes,
        "fontes_contexto": [
            {
                "documento": documento,
                "pagina": pagina,
            }
            for documento, pagina in sorted(fontes_contexto)
        ],
    }


def carregar_testes(versao, limite=None):
    """Carrega os resultados e separa respondíveis de não respondíveis."""

    caminho = ARQUIVOS_ENTRADA[versao]

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo de entrada não encontrado: {caminho}"
        )

    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    resultados = dados.get("resultados", [])

    if not resultados:
        raise ValueError(
            f"Nenhum resultado encontrado em {caminho.name}."
        )

    respondiveis = [
        teste for teste in resultados
        if (teste.get("tipo") or "").strip().lower()
        == "respondível"
    ]

    nao_respondiveis = [
        teste for teste in resultados
        if (teste.get("tipo") or "").strip().lower()
        != "respondível"
    ]

    if limite is not None:
        respondiveis = respondiveis[:limite]

    amostras = []
    metadados_testes = []

    for teste in respondiveis:
        identificador = teste.get("id", "sem_id")

        if teste.get("erro_contexto") or teste.get("erro_resposta"):
            raise ValueError(
                f"{identificador} possui erro no resultado original."
            )

        pergunta = (teste.get("pergunta") or "").strip()
        resposta_original = (
            teste.get("resposta_gerada") or ""
        ).strip()
        resposta_limpa = remover_citacoes(resposta_original)
        contextos = separar_contextos(
            teste.get("contexto_recuperado", "")
        )

        if not pergunta or not resposta_limpa:
            raise ValueError(
                f"{identificador} não possui pergunta ou resposta."
            )

        if not contextos:
            raise ValueError(
                f"{identificador} não possui contexto recuperado."
            )

        dados_citacoes = avaliar_citacoes(
            resposta_original,
            contextos,
        )

        # O RAGAS recebe o conteúdo factual sem os blocos de citação.
        amostras.append(
            SingleTurnSample(
                user_input=pergunta,
                response=resposta_limpa,
                retrieved_contexts=contextos,
            )
        )

        metadados_testes.append({
            "id": identificador,
            "tipo": teste.get("tipo"),
            "pergunta": pergunta,
            "resposta_original": resposta_original,
            "resposta_sem_citacoes": resposta_limpa,
            "avaliacao_citacoes": dados_citacoes,
        })

    if not amostras:
        raise ValueError(
            "Nenhum teste respondível foi encontrado para o RAGAS."
        )

    print(f"Versão do prompt: {versao}")
    print(f"Perguntas respondíveis para RAGAS: {len(amostras)}")
    print(
        "Perguntas não respondíveis separadas: "
        f"{len(nao_respondiveis)}"
    )

    return (
        amostras,
        metadados_testes,
        nao_respondiveis,
        caminho,
    )


def criar_avaliadores():
    """Inicializa os modelos avaliadores locais."""

    llm_langchain = ChatOllama(
        model=MODELO_AVALIADOR,
        base_url=OLLAMA_BASE_URL,
        temperature=0.0,
        num_predict=1024,
    )

    embeddings_langchain = OllamaEmbeddings(
        model=MODELO_EMBEDDINGS,
        base_url=OLLAMA_BASE_URL,
    )

    llm_avaliador = LangchainLLMWrapper(llm_langchain)
    embeddings_avaliador = LangchainEmbeddingsWrapper(
        embeddings_langchain
    )

    metricas = [
        Faithfulness(llm=llm_avaliador),
        ResponseRelevancy(
            llm=llm_avaliador,
            embeddings=embeddings_avaliador,
            strictness=3,
        ),
    ]

    return metricas


def numero_valido(valor):
    """Aceita apenas valores numéricos finitos."""

    return (
        isinstance(valor, (int, float))
        and not isinstance(valor, bool)
        and math.isfinite(valor)
    )


def executar_avaliacao(versao, limite=None):
    """Executa o RAGAS nos testes respondíveis e verifica citações."""

    (
        amostras,
        metadados_testes,
        nao_respondiveis,
        caminho_entrada,
    ) = carregar_testes(versao, limite)

    dataset = EvaluationDataset(samples=amostras)
    metricas = criar_avaliadores()

    config_execucao = RunConfig(
        timeout=300,
        max_retries=3,
        max_wait=15,
        max_workers=1,
        seed=42,
    )

    print("\nIniciando avaliação RAGAS...")
    print("Modelo avaliador:", MODELO_AVALIADOR)
    print("Métricas: Faithfulness e Answer Relevancy")
    print("Citações removidas somente da resposta avaliada.")
    print("Validação das citações: comparação documento/página.")

    resultado = evaluate(
        dataset=dataset,
        metrics=metricas,
        run_config=config_execucao,
        raise_exceptions=False,
        show_progress=True,
    )

    tabela = resultado.to_pandas()
    linhas_metricas = json.loads(
        tabela.to_json(
            orient="records",
            force_ascii=False,
        )
    )

    if len(linhas_metricas) != len(metadados_testes):
        raise RuntimeError(
            "A quantidade de resultados do RAGAS difere da "
            "quantidade de testes enviados."
        )

    resultados_finais = []

    for metadados, metricas_teste in zip(
        metadados_testes,
        linhas_metricas,
    ):
        resultados_finais.append({
            **metadados,
            "faithfulness": metricas_teste.get("faithfulness"),
            "answer_relevancy": metricas_teste.get(
                "answer_relevancy"
            ),
        })

    def valores_validos(nome):
        return [
            item[nome]
            for item in resultados_finais
            if numero_valido(item.get(nome))
        ]

    def media_metrica(nome):
        valores = valores_validos(nome)
        return mean(valores) if valores else None

    precisao_citacoes = [
        item["avaliacao_citacoes"]["precisao_referencias"]
        for item in resultados_finais
        if item["avaliacao_citacoes"]["quantidade_citacoes"] > 0
    ]

    resumo = {
        "framework": "RAGAS",
        "versao_ragas": version("ragas"),
        "versao_prompt": versao,
        "arquivo_entrada": caminho_entrada.name,
        "modelo_avaliador": MODELO_AVALIADOR,
        "modelo_embeddings_avaliador": MODELO_EMBEDDINGS,
        "provedor_avaliador": "Ollama local",
        "temperature_avaliador": 0.0,
        "max_workers": 1,
        "seed": 42,
        "quantidade_testes_original": (
            len(metadados_testes) + len(nao_respondiveis)
        ),
        "quantidade_testes_ragas": len(resultados_finais),
        "quantidade_nao_respondiveis_separados": len(nao_respondiveis),
        "quantidade_faithfulness_validas": len(
            valores_validos("faithfulness")
        ),
        "quantidade_answer_relevancy_validas": len(
            valores_validos("answer_relevancy")
        ),
        "faithfulness_media_respondiveis": media_metrica(
            "faithfulness"
        ),
        "answer_relevancy_media_respondiveis": media_metrica(
            "answer_relevancy"
        ),
        "precisao_media_citacoes_presentes_no_contexto": (
            mean(precisao_citacoes) if precisao_citacoes else None
        ),
        "metodo": (
            "Métricas RAGAS calculadas somente nas perguntas "
            "respondíveis, utilizando respostas sem blocos de citação. "
            "Referências documentais verificadas separadamente por "
            "presença de documento e página nos contextos recuperados. "
            "Perguntas não respondíveis ficam fora destas médias."
        ),
        "ids_nao_respondiveis_separados": [
            teste.get("id") for teste in nao_respondiveis
        ],
        "resultados": resultados_finais,
    }

    # Os arquivos anteriores são preservados.
    caminho_saida = (
        PASTA_RESULTADOS
        / f"ragas_prompt_{versao}_respondiveis.json"
    )

    with caminho_saida.open("w", encoding="utf-8") as arquivo:
        json.dump(
            resumo,
            arquivo,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )

    print("\nAVALIAÇÃO CONCLUÍDA")
    print("-" * 45)
    print("Testes originais:", resumo["quantidade_testes_original"])
    print("Testes avaliados pelo RAGAS:", resumo["quantidade_testes_ragas"])
    print(
        "Faithfulness média:",
        resumo["faithfulness_media_respondiveis"],
    )
    print(
        "Answer Relevancy média:",
        resumo["answer_relevancy_media_respondiveis"],
    )
    print(
        "Precisão média das citações verificadas:",
        resumo["precisao_media_citacoes_presentes_no_contexto"],
    )
    print(
        "Arquivo gerado:",
        caminho_saida,
    )

    return resumo


def main():
    parser = argparse.ArgumentParser(
        description="Avaliação RAGAS do GurAI com métricas separadas."
    )

    parser.add_argument(
        "--versao",
        choices=["v2", "v3", "ambos"],
        default="v2",
        help="Versão do prompt a avaliar. Padrão: v2.",
    )

    parser.add_argument(
        "--limite",
        type=int,
        default=1,
        help="Quantidade de testes respondíveis; use 0 para todos.",
    )

    args = parser.parse_args()

    if args.limite < 0:
        parser.error("--limite não pode ser negativo.")

    limite = args.limite if args.limite > 0 else None
    versoes = (
        ["v2", "v3"]
        if args.versao == "ambos"
        else [args.versao]
    )

    for versao in versoes:
        executar_avaliacao(versao, limite)


if __name__ == "__main__":
    main()
