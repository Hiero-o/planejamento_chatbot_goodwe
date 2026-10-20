
import json
from pathlib import Path
from statistics import mean


RAIZ = Path(__file__).resolve().parents[1]
PASTA_RESULTADOS = RAIZ / "evals" / "resultados"

ARQUIVOS_ENTRADA = {
    "v2": PASTA_RESULTADOS / "prompt_v2_retriever_corrigido.json",
    "v3": PASTA_RESULTADOS / "prompt_v3_retriever_corrigido.json",
}

ARQUIVOS_SAIDA = {
    "v2": (
        PASTA_RESULTADOS
        / "prompt_v2_retriever_corrigido_avaliado.json"
    ),
    "v3": (
        PASTA_RESULTADOS
        / "prompt_v3_retriever_corrigido_avaliado.json"
    ),
}

# Pontuações atribuídas manualmente após revisar as respostas
# e os contextos recuperados das duas versões.
PONTUACOES = {
    "rag_01": (1.0, 1.0),
    "rag_02": (1.0, 1.0),
    "rag_03": (1.0, 1.0),
    "rag_04": (1.0, 1.0),
    "rag_05": (1.0, 1.0),
    "rag_06": (1.0, 1.0),
    "rag_07": (1.0, 1.0),
    "rag_08": (1.0, 1.0),
    "rag_09": (1.0, 1.0),
    "rag_10": (1.0, 1.0),
}

JUSTIFICATIVAS = {
    "rag_01": (
        "A potência de 22.000 W confere com o contexto e "
        "a resposta cita o datasheet."
    ),
    "rag_02": (
        "A potência de 11.000 W confere com o contexto "
        "e a resposta apresenta uma citação documental."
    ),
    "rag_03": (
        "A tensão de saída de 400 V está sustentada "
        "pelos trechos recuperados e pela citação."
    ),
    "rag_04": (
        "A corrente nominal de saída de 32 A confere "
        "com os trechos documentais citados."
    ),
    "rag_05": (
        "A resposta identifica Modbus TCP e cita o manual "
        "na página que sustenta a informação."
    ),
    "rag_06": (
        "A resposta reconhece a ausência da velocidade de clock "
        "na documentação recuperada e não inventa um valor."
    ),
    "rag_07": (
        "A potência do modelo GW99K-HCA-20 não está comprovada "
        "no contexto, e a resposta evita inventá-la."
    ),
    "rag_08": (
        "O significado do código 999999 não foi encontrado "
        "nos trechos, e a resposta não inventa uma causa."
    ),
    "rag_09": (
        "A resposta distingue potência nominal de saída e "
        "potência máxima de carregamento, utiliza o trecho "
        "sobre OBC e cita as fontes pertinentes."
    ),
    "rag_10": (
        "A resposta não associa charger_01 a um modelo sem "
        "evidência e explica por que não pode confirmar "
        "a potência do equipamento."
    ),
}


def carregar_e_avaliar(versao, iteracao):
    """Carrega resultados reais e registra a avaliação manual."""

    entrada = ARQUIVOS_ENTRADA[versao]
    saida = ARQUIVOS_SAIDA[versao]

    if not entrada.exists():
        raise FileNotFoundError(
            f"Arquivo de resultados não encontrado: {entrada}"
        )

    with entrada.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    resultados = dados.get("resultados", [])

    if len(resultados) != len(PONTUACOES):
        raise ValueError(
            f"{versao}: eram esperados {len(PONTUACOES)} testes, "
            f"mas foram encontrados {len(resultados)}."
        )

    ids_encontrados = [item.get("id") for item in resultados]

    if len(set(ids_encontrados)) != len(ids_encontrados):
        raise ValueError(
            f"{versao}: há IDs de teste duplicados."
        )

    if set(ids_encontrados) != set(PONTUACOES):
        raise ValueError(
            f"{versao}: os IDs não correspondem ao conjunto "
            "de avaliação esperado."
        )

    for teste in resultados:
        identificador = teste["id"]

        if teste.get("erro_contexto") or teste.get("erro_resposta"):
            raise ValueError(
                f"{versao}: {identificador} possui erro técnico."
            )

        if not teste.get("resposta_gerada"):
            raise ValueError(
                f"{versao}: {identificador} não possui resposta."
            )

        faithfulness, answer_relevancy = PONTUACOES[identificador]

        justificativa = JUSTIFICATIVAS[identificador]

        teste["avaliacao_manual"] = {
            "faithfulness": faithfulness,
            "answer_relevancy": answer_relevancy,
            "justificativa_faithfulness": justificativa,
            "justificativa_answer_relevancy": justificativa,
        }

    # Corrige os metadados apenas na cópia avaliada.
    dados["experimento"] = (
        "Sprint 04 — comparação de prompts com retriever corrigido"
    )
    dados["iteracao"] = iteracao
    dados["versao_prompt"] = versao
    dados["metodo_avaliacao"] = (
        "Avaliação manual com rubrica de 0 a 1, baseada "
        "nas respostas geradas e nos contextos recuperados. "
        "Não corresponde a uma execução do RAGAS."
    )

    with saida.open("w", encoding="utf-8") as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )

    return {
        "versao": versao,
        "iteracao": iteracao,
        "quantidade_testes": len(resultados),
        "faithfulness": mean(
            PONTUACOES[item["id"]][0]
            for item in resultados
        ),
        "answer_relevancy": mean(
            PONTUACOES[item["id"]][1]
            for item in resultados
        ),
        "arquivo": saida.name,
        "resultados": resultados,
    }


def gerar_relatorio(avaliacoes):
    """Gera novos relatórios, sem sobrescrever os anteriores."""

    v2, v3 = avaliacoes

    ganho_fidelidade = v3["faithfulness"] - v2["faithfulness"]
    ganho_relevancia = (
        v3["answer_relevancy"] - v2["answer_relevancy"]
    )

    linhas = [
        "# Avaliação manual do RAG — comparação v2 × v3",
        "",
        "## Metodologia",
        "",
        "Foram avaliadas manualmente as respostas de dez perguntas "
        "documentais para cada versão do prompt, depois da correção "
        "do ranking do retriever.",
        "",
        "As notas variam de 0 a 1:",
        "",
        "- 1,0: resposta sustentada pelo contexto e adequada à pergunta.",
        "- 0,5: suporte ou atendimento parcial.",
        "- 0,0: afirmação não sustentada ou resposta inadequada.",
        "",
        "As métricas representam avaliação manual, e não scores "
        "calculados automaticamente pelo RAGAS.",
        "",
        "## Resultado por versão",
        "",
        "| Prompt | Testes | Faithfulness | Answer relevancy |",
        "|---|---:|---:|---:|",
    ]

    for avaliacao in avaliacoes:
        linhas.append(
            f"| {avaliacao['versao']} "
            f"| {avaliacao['quantidade_testes']} "
            f"| {avaliacao['faithfulness']:.3f} "
            f"| {avaliacao['answer_relevancy']:.3f} |"
        )

    linhas.extend([
        "",
        "## Comparação v2 × v3",
        "",
        f"- Variação em faithfulness: {ganho_fidelidade:+.3f}.",
        f"- Variação em answer relevancy: {ganho_relevancia:+.3f}.",
        "",
        "As versões empataram nas métricas deste conjunto de "
        "avaliação. Não foi demonstrada superioridade da v3.",
        "",
        "## Evolução do retriever",
        "",
        "Na avaliação preliminar, antes do ajuste do ranking, "
        "o rag_09 recebeu nota parcial porque o contexto final "
        "não continha a explicação sobre a limitação pelo OBC.",
        "Após a alteração do ranking, os trechos do manual na "
        "página 14 passaram a aparecer entre os primeiros "
        "resultados e as respostas passaram a explicar a "
        "influência do OBC com citações documentais.",
        "",
        "A média manual preliminar anterior era 0,950 em ambas "
        "as métricas. A média após a correção ficou em 1,000, "
        "uma diferença de +0,050. Esse resultado está associado "
        "à correção do retriever, não a uma vantagem isolada da v3.",
        "",
        "## Resultados por pergunta",
        "",
        "| Teste | Faithfulness v2 | Relevância v2 "
        "| Faithfulness v3 | Relevância v3 |",
        "|---|---:|---:|---:|---:|",
    ])

    mapa_v2 = {
        item["id"]: item
        for item in v2["resultados"]
    }
    mapa_v3 = {
        item["id"]: item
        for item in v3["resultados"]
    }

    for identificador in sorted(PONTUACOES):
        f2, r2 = PONTUACOES[identificador]
        f3, r3 = PONTUACOES[identificador]

        linhas.append(
            f"| {identificador} "
            f"| {f2:.1f} | {r2:.1f} "
            f"| {f3:.1f} | {r3:.1f} |"
        )

    linhas.extend([
        "",
        "## Limitações",
        "",
        "A avaliação utiliza dez perguntas e uma rubrica manual. "
        "As médias não garantem desempenho geral para perguntas "
        "fora desse conjunto.",
        "A avaliação do prompt e a avaliação do retriever devem "
        "permanecer separadas para não atribuir a uma mudança "
        "um ganho produzido por outra.",
        "Neste projeto, os embeddings são gerados localmente pelo "
        "Ollama usando o modelo nomic-embed-text, com "
        "RAG_EMBEDDING_PROVIDER=local. Essa escolha é intencional "
        "e está alinhada à preferência do professor. O provedor de "
        "embeddings é independente do provedor do modelo generativo: "
        "o GurAI pode utilizar o gemma4:31b-cloud para gerar respostas "
        "e manter a geração de embeddings na máquina local.",
    ])

    caminho_md = (
        PASTA_RESULTADOS
        / "comparacao_prompts_v2_v3_retriever_corrigido.md"
    )
    caminho_md.write_text("\n".join(linhas), encoding="utf-8")

    resumo = {
        "metodo": "avaliação manual",
        "quantidade_testes_por_versao": len(PONTUACOES),
        "versoes": [
            {
                "versao": item["versao"],
                "iteracao": item["iteracao"],
                "faithfulness_media": item["faithfulness"],
                "answer_relevancy_media": item["answer_relevancy"],
                "arquivo_avaliado": item["arquivo"],
            }
            for item in avaliacoes
        ],
        "variacao_faithfulness_v3_menos_v2": ganho_fidelidade,
        "variacao_answer_relevancy_v3_menos_v2": ganho_relevancia,
        "observacao": (
            "O ganho preliminar após o ajuste do ranking do retriever "
            "não deve ser atribuído exclusivamente à versão do prompt."
        ),
    }

    caminho_json = (
        PASTA_RESULTADOS
        / "comparacao_prompts_v2_v3_retriever_corrigido.json"
    )

    with caminho_json.open("w", encoding="utf-8") as arquivo:
        json.dump(
            resumo,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )

    return caminho_md, caminho_json


def main():
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    print("Avaliando resultados com o retriever corrigido...")

    v2 = carregar_e_avaliar("v2", 1)
    v3 = carregar_e_avaliar("v3", 2)

    avaliacoes = [v2, v3]
    caminho_md, caminho_json = gerar_relatorio(avaliacoes)

    print("\nRESULTADOS")
    print("-" * 50)

    for item in avaliacoes:
        print(f"Prompt: {item['versao']}")
        print(f"Testes: {item['quantidade_testes']}")
        print(f"Faithfulness: {item['faithfulness']:.3f}")
        print(f"Answer relevancy: {item['answer_relevancy']:.3f}")
        print(f"Arquivo avaliado: {item['arquivo']}")
        print()

    print("Relatório:", caminho_md)
    print("Resumo JSON:", caminho_json)
    print("\nAvaliação concluída.")


if __name__ == "__main__":
    main()
