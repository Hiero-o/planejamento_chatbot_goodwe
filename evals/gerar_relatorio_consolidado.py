
import json
import math
from pathlib import Path
from statistics import mean


RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "evals" / "resultados"

ARQUIVOS = {
    "v2_original": PASTA / "prompt_v2_retriever_corrigido.json",
    "v3_original": PASTA / "prompt_v3_retriever_corrigido.json",
    "v2_ragas": PASTA / "ragas_prompt_v2_respondiveis.json",
    "v3_ragas": PASTA / "ragas_prompt_v3_respondiveis.json",
    "v2_completo": PASTA / "ragas_prompt_v2_sequencial.json",
    "v3_completo": PASTA / "ragas_prompt_v3_sequencial.json",
}

ARQUIVO_RELATORIO = PASTA / "relatorio_consolidado_avaliacao.md"
ARQUIVO_RESUMO = PASTA / "relatorio_consolidado_avaliacao.json"

METRICAS = {
    "faithfulness": "Faithfulness",
    "answer_relevancy": "Answer Relevancy",
}

# Resultado da revisão manual das quatro perguntas não respondíveis.
# A avaliação deve permanecer documentada como manual.
AVALIACAO_RECUSAS = {
    "rag_06": (
        "Correta",
        "A resposta informa que a velocidade de clock não foi "
        "encontrada na documentação.",
    ),
    "rag_07": (
        "Correta",
        "A resposta não inventa uma potência para o modelo "
        "GW99K-HCA-20, que não está documentado na base.",
    ),
    "rag_08": (
        "Correta",
        "A resposta informa que o significado do código de erro "
        "999999 não foi encontrado.",
    ),
    "rag_10": (
        "Correta",
        "A resposta não associa charger_01 a um modelo específico "
        "sem uma relação documentada.",
    ),
}


def carregar_json(caminho):
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo necessário não encontrado: {caminho}"
        )

    with caminho.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def indexar_resultados(dados, descricao):
    resultados = dados.get("resultados", [])

    if not resultados:
        raise ValueError(
            f"Nenhum resultado encontrado em {descricao}."
        )

    indexados = {}

    for item in resultados:
        identificador = item.get("id")

        if not identificador:
            raise ValueError(
                f"Resultado sem ID em {descricao}."
            )

        if identificador in indexados:
            raise ValueError(
                f"ID duplicado {identificador} em {descricao}."
            )

        indexados[identificador] = item

    return indexados


def numero_valido(valor):
    return (
        isinstance(valor, (int, float))
        and not isinstance(valor, bool)
        and math.isfinite(valor)
    )


def formatar(valor):
    if not numero_valido(valor):
        return "N/D"

    return f"{valor:.3f}"


def calcular_media(itens, campo):
    valores = [
        item.get(campo)
        for item in itens
        if numero_valido(item.get(campo))
    ]

    return mean(valores) if valores else None


def texto_curto(texto, limite=230):
    texto = " ".join(str(texto or "").split())

    if len(texto) > limite:
        return texto[:limite - 3] + "..."

    return texto


def avaliar_citacoes(itens):
    """Resume a checagem documental já calculada pelo script RAGAS."""

    precisao_por_resposta = []
    total_citacoes = 0
    citacoes_presentes = 0
    respostas_com_citacoes = 0
    respostas_sem_citacoes = 0

    for item in itens:
        avaliacao = item.get("avaliacao_citacoes") or {}

        quantidade = avaliacao.get("quantidade_citacoes", 0)
        quantidade_valida = avaliacao.get(
            "quantidade_citacoes_presentes_no_contexto", 0
        )
        precisao = avaliacao.get("precisao_referencias")

        if not isinstance(quantidade, int):
            quantidade = 0

        if not isinstance(quantidade_valida, int):
            quantidade_valida = 0

        if quantidade > 0:
            respostas_com_citacoes += 1
            total_citacoes += quantidade
            citacoes_presentes += quantidade_valida

            if numero_valido(precisao):
                precisao_por_resposta.append(precisao)
        else:
            respostas_sem_citacoes += 1

    return {
        "respostas_com_citacoes": respostas_com_citacoes,
        "respostas_sem_citacoes": respostas_sem_citacoes,
        "total_citacoes": total_citacoes,
        "citacoes_presentes_nos_contextos": citacoes_presentes,
        "precisao_micro_citacoes": (
            citacoes_presentes / total_citacoes
            if total_citacoes
            else None
        ),
        "precisao_media_por_resposta": (
            mean(precisao_por_resposta)
            if precisao_por_resposta
            else None
        ),
        "observacao": (
            "Verifica se documento e página citados aparecem nos "
            "contextos recuperados. Não comprova, isoladamente, "
            "que todo o conteúdo da resposta é sustentado pela fonte."
        ),
    }


def validar_entradas(originais, ragas, versao):
    ids_originais = set(originais)
    ids_ragas = set(ragas)

    respondiveis = {
        identificador
        for identificador, item in originais.items()
        if item.get("tipo") == "respondível"
    }

    nao_respondiveis = {
        identificador
        for identificador, item in originais.items()
        if item.get("tipo") == "não_respondível"
    }

    if not respondiveis or not nao_respondiveis:
        raise ValueError(
            f"{versao}: classificação dos testes ausente ou inesperada."
        )

    if ids_ragas != respondiveis:
        faltantes = sorted(respondiveis - ids_ragas)
        extras = sorted(ids_ragas - respondiveis)

        raise ValueError(
            f"{versao}: IDs do RAGAS não correspondem aos testes "
            f"respondíveis. Faltantes={faltantes}; extras={extras}"
        )

    ids_recusas = set(AVALIACAO_RECUSAS)

    if nao_respondiveis != ids_recusas:
        raise ValueError(
            f"{versao}: os IDs não respondíveis mudaram. "
            "Revise as avaliações manuais antes de gerar o relatório."
        )

    for identificador in nao_respondiveis:
        resposta = originais[identificador].get("resposta_gerada", "")

        if not resposta.strip():
            raise ValueError(
                f"{versao}: resposta ausente em {identificador}."
            )

    return respondiveis, nao_respondiveis


def construir_resumo(dados):
    resumo_versoes = {}
    indexados = {}

    for versao in ("v2", "v3"):
        originais = indexar_resultados(
            dados[f"{versao}_original"],
            f"resultados originais {versao}",
        )
        ragas = indexar_resultados(
            dados[f"{versao}_ragas"],
            f"resultados RAGAS respondíveis {versao}",
        )

        respondiveis, nao_respondiveis = validar_entradas(
            originais,
            ragas,
            versao,
        )

        resultados_ragas = list(ragas.values())

        metricas = {}

        for chave, nome in METRICAS.items():
            metricas[chave] = {
                "nome": nome,
                "media": calcular_media(resultados_ragas, chave),
                "notas_validas": sum(
                    numero_valido(item.get(chave))
                    for item in resultados_ragas
                ),
                "total_testes": len(resultados_ragas),
            }

        recusas = []

        for identificador in sorted(nao_respondiveis):
            situacao, justificativa = AVALIACAO_RECUSAS[identificador]

            recusas.append({
                "id": identificador,
                "pergunta": originais[identificador].get("pergunta"),
                "resposta": originais[identificador].get(
                    "resposta_gerada"
                ),
                "avaliacao_manual": situacao,
                "justificativa": justificativa,
            })

        citacoes = avaliar_citacoes(resultados_ragas)

        # Rodada anterior com todos os dez testes:
        # mantida como análise exploratória, sem misturá-la
        # às métricas principais das perguntas respondíveis.
        completo = dados[f"{versao}_completo"]

        resumo_versoes[versao] = {
            "total_testes": len(originais),
            "testes_respondiveis": len(respondiveis),
            "testes_nao_respondiveis": len(nao_respondiveis),
            "metricas_ragas_respondiveis": metricas,
            "verificacao_citacoes": citacoes,
            "recusas_avaliadas_manualmente": recusas,
            "total_recusas_corretas": sum(
                item["avaliacao_manual"] == "Correta"
                for item in recusas
            ),
            "taxa_recusas_corretas": (
                sum(
                    item["avaliacao_manual"] == "Correta"
                    for item in recusas
                ) / len(recusas)
                if recusas
                else None
            ),
            "rodada_exploratoria_dez_testes": {
                "faithfulness_media": completo.get("faithfulness_media"),
                "faithfulness_notas_validas": completo.get(
                    "quantidade_faithfulness_validas"
                ),
                "answer_relevancy_media": completo.get(
                    "answer_relevancy_media"
                ),
                "answer_relevancy_notas_validas": completo.get(
                    "quantidade_answer_relevancy_validas"
                ),
                "observacao": (
                    "Rodada exploratória com os dez testes misturados. "
                    "Não é a métrica principal da comparação por combinar "
                    "respostas factuais e recusas."
                ),
            },
        }

        indexados[versao] = {
            "originais": originais,
            "ragas": ragas,
        }

    diferencas = {}

    for chave, nome in METRICAS.items():
        media_v2 = resumo_versoes["v2"][
            "metricas_ragas_respondiveis"
        ][chave]["media"]

        media_v3 = resumo_versoes["v3"][
            "metricas_ragas_respondiveis"
        ][chave]["media"]

        diferencas[chave] = {
            "nome": nome,
            "media_v2": media_v2,
            "media_v3": media_v3,
            "diferenca_v3_menos_v2": (
                media_v3 - media_v2
                if numero_valido(media_v2)
                and numero_valido(media_v3)
                else None
            ),
        }

    return {
        "titulo": "Avaliação consolidada do RAG GurAI — Sprint 04",
        "metodo": {
            "avaliacao_automatica": (
                "RAGAS 0.4.3 com Llama 3 e nomic-embed-text locais."
            ),
            "testes_respondiveis": (
                "Faithfulness e Answer Relevancy calculadas "
                "automaticamente nos seis casos respondíveis."
            ),
            "testes_nao_respondiveis": (
                "Revisão manual da correção das recusas, mantendo "
                "as quatro perguntas na contagem geral."
            ),
            "citacoes": (
                "Checagem determinística da presença de documento e "
                "página citados nos contextos recuperados."
            ),
        },
        "comparacao_v2_v3": diferencas,
        "versoes": resumo_versoes,
        "limitacoes": [
            "O conjunto contém dez perguntas e é pequeno.",
            "O Llama 3 usado como avaliador pode cometer erros.",
            "A presença de uma citação no contexto não comprova "
            "automaticamente todas as afirmações da resposta.",
            "A revisão das recusas é manual e não constitui uma "
            "métrica automática RAGAS.",
            "A comparação não prova generalização para perguntas "
            "fora do conjunto avaliado.",
        ],
    }


def gerar_markdown(resumo, dados_originais):
    v2 = resumo["versoes"]["v2"]
    v3 = resumo["versoes"]["v3"]

    linhas = [
        "# Avaliação consolidada do RAG GurAI — Sprint 04",
        "",
        "## 1. Escopo e metodologia",
        "",
        "O conjunto de avaliação contém dez perguntas fixas: seis "
        "respondíveis e quatro não respondíveis. Nenhuma pergunta "
        "foi excluída por ter obtido uma nota baixa.",
        "",
        "As seis perguntas respondíveis são avaliadas com RAGAS 0.4.3 "
        "usando o Llama 3 local como juiz e nomic-embed-text local "
        "na métrica de relevância. As quatro recusas são revisadas "
        "manualmente, pois uma recusa correta não deve ser tratada "
        "simplesmente como uma resposta factual comum.",
        "",
        "As referências são verificadas separadamente pela presença "
        "do documento e da página citados nos contextos recuperados.",
        "",
        "## 2. Resultados principais: perguntas respondíveis",
        "",
        "| Métrica | v2 | v3 | Diferença v3 - v2 |",
        "|---|---:|---:|---:|",
    ]

    for chave, item in resumo["comparacao_v2_v3"].items():
        linhas.append(
            f"| {item['nome']} "
            f"| {formatar(item['media_v2'])} "
            f"| {formatar(item['media_v3'])} "
            f"| {formatar(item['diferenca_v3_menos_v2'])} |"
        )

    linhas.extend([
        "",
        "## 3. Resultados por pergunta",
        "",
        "| ID | Faithfulness v2 | Faithfulness v3 "
        "| Relevância v2 | Relevância v3 |",
        "|---|---:|---:|---:|---:|",
    ])

    v2_ragas = indexar_resultados(
        dados_originais["v2_ragas"],
        "RAGAS v2",
    )
    v3_ragas = indexar_resultados(
        dados_originais["v3_ragas"],
        "RAGAS v3",
    )

    for identificador in sorted(v2_ragas):
        a = v2_ragas[identificador]
        b = v3_ragas[identificador]

        linhas.append(
            f"| {identificador} "
            f"| {formatar(a.get('faithfulness'))} "
            f"| {formatar(b.get('faithfulness'))} "
            f"| {formatar(a.get('answer_relevancy'))} "
            f"| {formatar(b.get('answer_relevancy'))} |"
        )

    linhas.extend([
        "",
        "## 4. Verificação de citações",
        "",
        "| Resultado | v2 | v3 |",
        "|---|---:|---:|",
    ])

    for chave, titulo in [
        ("precisao_micro_citacoes", "Precisão micro das citações"),
        ("precisao_media_por_resposta", "Precisão média por resposta"),
    ]:
        a = v2["verificacao_citacoes"][chave]
        b = v3["verificacao_citacoes"][chave]
        linhas.append(
            f"| {titulo} | {formatar(a)} | {formatar(b)} |"
        )

    linhas.extend([
        "",
        "A verificação confirma somente se o par documento/página "
        "está presente nos contextos recuperados; não valida "
        "semanticamente todo o conteúdo da resposta.",
        "",
        "## 5. Perguntas não respondíveis e recusas",
        "",
        "| ID | Avaliação v2 | Avaliação v3 |",
        "|---|---|---|",
    ])

    for item_v2, item_v3 in zip(
        v2["recusas_avaliadas_manualmente"],
        v3["recusas_avaliadas_manualmente"],
    ):
        linhas.append(
            f"| {item_v2['id']} "
            f"| {item_v2['avaliacao_manual']} "
            f"| {item_v3['avaliacao_manual']} |"
        )

    linhas.extend([
        "",
        f"- v2: {v2['total_recusas_corretas']}/"
        f"{v2['testes_nao_respondiveis']} recusas corretas.",
        f"- v3: {v3['total_recusas_corretas']}/"
        f"{v3['testes_nao_respondiveis']} recusas corretas.",
        "",
        "As notas das recusas são avaliações manuais, não métricas "
        "calculadas pelo RAGAS.",
        "",
        "## 6. Rodada exploratória com os dez testes",
        "",
        "| Métrica | v2 | v3 |",
        "|---|---:|---:|",
        (
            "| Faithfulness média | "
            f"{formatar(v2['rodada_exploratoria_dez_testes']['faithfulness_media'])} | "
            f"{formatar(v3['rodada_exploratoria_dez_testes']['faithfulness_media'])} |"
        ),
        (
            "| Answer Relevancy média | "
            f"{formatar(v2['rodada_exploratoria_dez_testes']['answer_relevancy_media'])} | "
            f"{formatar(v3['rodada_exploratoria_dez_testes']['answer_relevancy_media'])} |"
        ),
        "",
        "Esta rodada é mantida para transparência, mas não é a "
        "comparação principal: ela combina perguntas factuais e "
        "perguntas em que a resposta correta é uma recusa. Além disso, "
        "uma avaliação individual da fidelidade da v3 falhou em uma "
        "execução exploratória anterior.",
        "",
        "## 7. Interpretação",
        "",
        "Neste conjunto pequeno, a v3 obteve Faithfulness média maior "
        "nas seis perguntas respondíveis, enquanto Answer Relevancy "
        "permaneceu praticamente empatada. Os quatro casos de recusa "
        "foram considerados corretos nas duas versões pela revisão "
        "manual.",
        "",
        "Esses resultados não provam superioridade geral da v3. O "
        "avaliador é um modelo local, pode cometer erros e a amostra "
        "é pequena. São necessários mais testes para avaliar "
        "generalização e consistência.",
        "",
        "## 8. Limitações",
        "",
    ])

    for limitacao in resumo["limitacoes"]:
        linhas.append(f"- {limitacao}")

    linhas.append("")
    return "\n".join(linhas)


def main():
    PASTA.mkdir(parents=True, exist_ok=True)

    dados = {
        nome: carregar_json(caminho)
        for nome, caminho in ARQUIVOS.items()
    }

    resumo = construir_resumo(dados)
    markdown = gerar_markdown(resumo, dados)

    ARQUIVO_RELATORIO.write_text(
        markdown,
        encoding="utf-8",
    )

    with ARQUIVO_RESUMO.open("w", encoding="utf-8") as arquivo:
        json.dump(
            resumo,
            arquivo,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )

    print("RELATÓRIO CONSOLIDADO GERADO")
    print("-" * 55)

    for versao in ("v2", "v3"):
        dados_versao = resumo["versoes"][versao]
        metricas = dados_versao["metricas_ragas_respondiveis"]

        print(f"\nPrompt {versao}:")
        print(
            "Faithfulness:",
            formatar(metricas["faithfulness"]["media"]),
        )
        print(
            "Answer Relevancy:",
            formatar(metricas["answer_relevancy"]["media"]),
        )
        print(
            "Recusas corretas:",
            f"{dados_versao['total_recusas_corretas']}/"
            f"{dados_versao['testes_nao_respondiveis']}",
        )
        print(
            "Precisão média das citações:",
            formatar(
                dados_versao["verificacao_citacoes"][
                    "precisao_media_por_resposta"
                ]
            ),
        )

    print("\nMarkdown:", ARQUIVO_RELATORIO)
    print("JSON:", ARQUIVO_RESUMO)


if __name__ == "__main__":
    main()
