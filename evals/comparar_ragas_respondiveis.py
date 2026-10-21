
import json
import math
from pathlib import Path
from statistics import mean


RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "evals" / "resultados"

ARQUIVOS = {
    "v2": PASTA / "ragas_prompt_v2_respondiveis.json",
    "v3": PASTA / "ragas_prompt_v3_respondiveis.json",
}


def valido(valor):
    return (
        isinstance(valor, (int, float))
        and not isinstance(valor, bool)
        and math.isfinite(valor)
    )


def carregar(versao):
    caminho = ARQUIVOS[versao]

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    resultados = dados.get("resultados", [])
    por_id = {item["id"]: item for item in resultados}

    if len(por_id) != len(resultados):
        raise ValueError(f"IDs duplicados no arquivo da versão {versao}.")

    return dados, por_id


def media(por_id, ids, metrica):
    valores = [
        por_id[identificador][metrica]
        for identificador in ids
        if valido(por_id[identificador].get(metrica))
    ]

    return mean(valores) if valores else None


def fmt(valor):
    return f"{valor:.3f}" if valido(valor) else "N/D"


def main():
    dados_v2, v2 = carregar("v2")
    dados_v3, v3 = carregar("v3")

    ids = sorted(set(v2) & set(v3))

    if not ids:
        raise ValueError("As versões não têm testes em comum.")

    metricas = [
        ("faithfulness", "Faithfulness"),
        ("answer_relevancy", "Answer Relevancy"),
    ]

    print("\nCOMPARAÇÃO RAGAS — TESTES RESPONDÍVEIS")
    print("=" * 76)

    for identificador in ids:
        item_v2 = v2[identificador]
        item_v3 = v3[identificador]

        print(f"\n{identificador}")
        print("Pergunta:", item_v2.get("pergunta", ""))

        for chave, nome in metricas:
            nota_v2 = item_v2.get(chave)
            nota_v3 = item_v3.get(chave)

            diferenca = (
                nota_v3 - nota_v2
                if valido(nota_v2) and valido(nota_v3)
                else None
            )

            print(
                f"{nome}: v2={fmt(nota_v2)} | "
                f"v3={fmt(nota_v3)} | "
                f"diferença={fmt(diferenca)}"
            )

    print("\nMÉDIAS DO CONJUNTO")
    print("-" * 76)

    resumo = {
        "metodo": "Comparação pareada dos resultados RAGAS",
        "versao_ragas": dados_v2.get("versao_ragas"),
        "quantidade_ids_em_comum": len(ids),
        "ids_comparados": ids,
        "medias": {},
    }

    for chave, nome in metricas:
        media_v2 = media(v2, ids, chave)
        media_v3 = media(v3, ids, chave)

        diferenca = (
            media_v3 - media_v2
            if media_v2 is not None and media_v3 is not None
            else None
        )

        resumo["medias"][chave] = {
            "nome": nome,
            "v2": media_v2,
            "v3": media_v3,
            "diferenca_v3_menos_v2": diferenca,
        }

        print(
            f"{nome}: v2={fmt(media_v2)} | "
            f"v3={fmt(media_v3)} | "
            f"diferença={fmt(diferenca)}"
        )

    linhas = [
        "# Comparação RAGAS — perguntas respondíveis",
        "",
        f"Quantidade de perguntas em comum: {len(ids)}",
        "",
        "## Notas por pergunta",
        "",
        "| ID | Faithfulness v2 | Faithfulness v3 "
        "| Relevância v2 | Relevância v3 |",
        "|---|---:|---:|---:|---:|",
    ]

    for identificador in ids:
        a = v2[identificador]
        b = v3[identificador]

        linhas.append(
            f"| {identificador} "
            f"| {fmt(a.get('faithfulness'))} "
            f"| {fmt(b.get('faithfulness'))} "
            f"| {fmt(a.get('answer_relevancy'))} "
            f"| {fmt(b.get('answer_relevancy'))} |"
        )

    linhas.extend([
        "",
        "## Médias",
        "",
        "| Métrica | v2 | v3 | Diferença v3 - v2 |",
        "|---|---:|---:|---:|",
    ])

    for chave, nome in metricas:
        item = resumo["medias"][chave]
        linhas.append(
            f"| {nome} | {fmt(item['v2'])} "
            f"| {fmt(item['v3'])} "
            f"| {fmt(item['diferenca_v3_menos_v2'])} |"
        )

    linhas.extend([
        "",
        "## Limitações",
        "",
        "A análise compara os mesmos IDs e usa os resultados "
        "RAGAS já calculados. A diferença observada não prova "
        "superioridade geral de uma versão: o conjunto é pequeno "
        "e o modelo avaliador pode cometer erros.",
        "",
    ])

    caminho_md = PASTA / "comparacao_ragas_respondiveis.md"
    caminho_json = PASTA / "comparacao_ragas_respondiveis.json"

    caminho_md.write_text("\n".join(linhas), encoding="utf-8")

    with caminho_json.open("w", encoding="utf-8") as arquivo:
        json.dump(
            resumo,
            arquivo,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )

    print("\nRelatório Markdown:", caminho_md)
    print("Resumo JSON:", caminho_json)


if __name__ == "__main__":
    main()
