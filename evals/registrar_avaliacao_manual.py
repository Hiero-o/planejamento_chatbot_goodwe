
import json
from pathlib import Path
from statistics import mean


RAIZ = Path(__file__).resolve().parents[1]
PASTA_EVALS = RAIZ / "evals"

# Pontuações manuais definidas após revisar as respostas
# e os respectivos contextos recuperados.
PONTUACOES = {
    1: {
        **{
            f"rag_{numero:02d}": (1.0, 1.0)
            for numero in range(1, 8)
        },
        "rag_08": (0.0, 0.0),
    },
    2: {
        f"rag_{numero:02d}": (1.0, 1.0)
        for numero in range(1, 9)
    },
}


def criar_justificativas(teste, iteracao):
    identificador = teste["id"]

    if identificador == "rag_08" and iteracao == 1:
        return {
            "justificativa_faithfulness": (
                "A resposta classificou incorretamente uma "
                "pergunta técnica sobre códigos de erro como "
                "fora do escopo. Essa conclusão não foi "
                "sustentada pelo contexto recuperado."
            ),
            "justificativa_answer_relevancy": (
                "A resposta não tratou da ausência de "
                "informação sobre o código solicitado e "
                "desviou da pergunta."
            ),
        }

    if teste["tipo"] == "respondível":
        return {
            "justificativa_faithfulness": (
                "A informação principal da resposta confere "
                "com o contexto recuperado. A resposta "
                "documental apresenta citação de fonte."
            ),
            "justificativa_answer_relevancy": (
                "A resposta atende diretamente à pergunta "
                "e fornece a informação solicitada."
            ),
        }

    if identificador == "rag_06":
        justificativa = (
            "A resposta reconhece que a velocidade de clock "
            "não foi encontrada no contexto recuperado e "
            "não inventa uma especificação."
        )
    elif identificador == "rag_07":
        justificativa = (
            "O contexto apresenta modelos diferentes, mas "
            "não comprova a potência do GW99K-HCA-20. "
            "A resposta evita inventar esse dado."
        )
    else:
        justificativa = (
            "A resposta reconhece que o significado do "
            "código solicitado não está comprovado nos "
            "trechos recuperados, sem inventar uma causa."
        )

    return {
        "justificativa_faithfulness": justificativa,
        "justificativa_answer_relevancy": (
            "A resposta trata diretamente da informação "
            "solicitada, explicando que não foi possível "
            "confirmá-la na documentação recuperada."
        ),
    }


def carregar_resultado(iteracao):
    caminho = (
        PASTA_EVALS
        / f"resultados_rag_iteracao_{iteracao}.json"
    )

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    resultados = dados.get("resultados", [])

    if not resultados:
        raise ValueError(
            f"O arquivo da iteração {iteracao} não contém resultados."
        )

    pontuacoes = PONTUACOES[iteracao]
    identificadores = {item["id"] for item in resultados}

    ausentes = set(pontuacoes) - identificadores
    if ausentes:
        raise ValueError(
            f"Testes ausentes na iteração {iteracao}: "
            f"{sorted(ausentes)}"
        )

    for teste in resultados:
        identificador = teste["id"]

        # Não pontuar respostas que falharam tecnicamente.
        if (
            teste.get("erro_contexto")
            or teste.get("erro_resposta")
            or not teste.get("resposta_gerada")
        ):
            raise ValueError(
                f"{identificador} possui erro técnico ou "
                "não contém resposta. Corrija antes de pontuar."
            )

        faithfulness, answer_relevancy = pontuacoes[
            identificador
        ]

        justificativas = criar_justificativas(
            teste,
            iteracao,
        )

        teste["avaliacao_manual"] = {
            "faithfulness": faithfulness,
            "answer_relevancy": answer_relevancy,
            **justificativas,
        }

    # Garante que o número da iteração corresponda ao arquivo.
    dados["iteracao"] = iteracao
    dados["metodo_avaliacao"] = (
        "Avaliação manual baseada no contexto recuperado, "
        "na resposta gerada e na rubrica documentada."
    )

    caminho_saida = (
        PASTA_EVALS
        / f"resultados_rag_iteracao_{iteracao}_avaliado.json"
    )

    with caminho_saida.open("w", encoding="utf-8") as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )

    valores_fidelidade = [
        item["avaliacao_manual"]["faithfulness"]
        for item in resultados
    ]
    valores_relevancia = [
        item["avaliacao_manual"]["answer_relevancy"]
        for item in resultados
    ]

    return {
        "iteracao": iteracao,
        "quantidade": len(resultados),
        "faithfulness": mean(valores_fidelidade),
        "answer_relevancy": mean(valores_relevancia),
        "arquivo": caminho_saida.name,
        "resultados": resultados,
    }


def gerar_relatorio(resumos):
    primeira = resumos[0]
    segunda = resumos[1]

    ganho_fidelidade = (
        segunda["faithfulness"] - primeira["faithfulness"]
    )
    ganho_relevancia = (
        segunda["answer_relevancy"]
        - primeira["answer_relevancy"]
    )

    linhas = [
        "# Relatório de avaliação manual do RAG — GurAI",
        "",
        "## Metodologia",
        "",
        "Foi aplicado o mesmo conjunto de perguntas "
        "documentais nas duas execuções.",
        "As notas variam de 0 a 1 e foram atribuídas "
        "manualmente após inspeção das respostas e dos "
        "contextos recuperados.",
        "",
        "- Faithfulness: fidelidade das afirmações ao contexto.",
        "- Answer relevancy: pertinência da resposta à pergunta.",
        "- A qualidade das citações deve também ser "
        "verificada separadamente.",
        "",
        "Esta avaliação é um fallback manual, não uma "
        "execução do RAGAS.",
        "",
        "## Resultados gerais",
        "",
        "| Iteração | Faithfulness média | Answer relevancy média |",
        "|---|---:|---:|",
    ]

    for resumo in resumos:
        linhas.append(
            f"| {resumo['iteracao']} "
            f"| {resumo['faithfulness']:.3f} "
            f"| {resumo['answer_relevancy']:.3f} |"
        )

    linhas.extend([
        "",
        "## Comparação antes e depois",
        "",
        f"- Ganho em faithfulness: {ganho_fidelidade:+.3f} "
        f"({ganho_fidelidade * 100:+.1f} pontos percentuais).",
        f"- Ganho em answer_relevancy: {ganho_relevancia:+.3f} "
        f"({ganho_relevancia * 100:+.1f} pontos percentuais).",
        "",
        "## Pontuação por pergunta",
        "",
        "| Teste | Faithfulness I1 | Relevância I1 "
        "| Faithfulness I2 | Relevância I2 |",
        "|---|---:|---:|---:|---:|",
    ])

    resultados_por_iteracao = [
        {
            item["id"]: item
            for item in resumo["resultados"]
        }
        for resumo in resumos
    ]

    ids = sorted(resultados_por_iteracao[0])

    for identificador in ids:
        primeira_avaliacao = resultados_por_iteracao[0][
            identificador
        ]["avaliacao_manual"]

        segunda_avaliacao = resultados_por_iteracao[1][
            identificador
        ]["avaliacao_manual"]

        linhas.append(
            f"| {identificador} "
            f"| {primeira_avaliacao['faithfulness']:.1f} "
            f"| {primeira_avaliacao['answer_relevancy']:.1f} "
            f"| {segunda_avaliacao['faithfulness']:.1f} "
            f"| {segunda_avaliacao['answer_relevancy']:.1f} |"
        )

    linhas.extend([
        "",
        "## Interpretação",
        "",
        "A principal mudança avaliada foi a correção do falso "
        "bloqueio da pergunta sobre o código de erro 999999. "
        "A segunda execução passou a responder com uma "
        "abstenção apropriada.",
        "",
        "O ganho está relacionado ao comportamento do "
        "guardrail e à pertinência da resposta. Ele não "
        "demonstra, isoladamente, melhoria na recuperação "
        "documental ou no prompt RAG.",
        "",
        "As versões e os parâmetros do pipeline precisam ser "
        "registrados separadamente para completar a análise "
        "de evolução exigida pela Sprint 04.",
        "",
    ])

    caminho = PASTA_EVALS / "relatorio_avaliacao_manual.md"
    caminho.write_text("\n".join(linhas), encoding="utf-8")

    resumo_json = {
        "metodo": "fallback manual",
        "iteracoes": [
            {
                "iteracao": resumo["iteracao"],
                "quantidade_testes": resumo["quantidade"],
                "faithfulness_media": resumo["faithfulness"],
                "answer_relevancy_media": resumo[
                    "answer_relevancy"
                ],
                "arquivo_avaliado": resumo["arquivo"],
            }
            for resumo in resumos
        ],
        "ganho_faithfulness": ganho_fidelidade,
        "ganho_answer_relevancy": ganho_relevancia,
    }

    caminho_json = (
        PASTA_EVALS / "resumo_avaliacao_manual.json"
    )

    with caminho_json.open("w", encoding="utf-8") as arquivo:
        json.dump(
            resumo_json,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )

    return caminho, caminho_json


def main():
    PASTA_EVALS.mkdir(parents=True, exist_ok=True)

    print("Registrando avaliações manuais do GurAI...")

    resumos = [
        carregar_resultado(1),
        carregar_resultado(2),
    ]

    caminho_md, caminho_json = gerar_relatorio(resumos)

    print("\nRESULTADOS")
    print("-" * 50)

    for resumo in resumos:
        print(f"Iteração: {resumo['iteracao']}")
        print(f"Testes: {resumo['quantidade']}")
        print(
            "Faithfulness média: "
            f"{resumo['faithfulness']:.3f}"
        )
        print(
            "Answer relevancy média: "
            f"{resumo['answer_relevancy']:.3f}"
        )
        print(f"Arquivo: {resumo['arquivo']}")
        print()

    print("Relatório:", caminho_md)
    print("Resumo JSON:", caminho_json)
    print("\nAvaliação registrada com sucesso.")


if __name__ == "__main__":
    main()
