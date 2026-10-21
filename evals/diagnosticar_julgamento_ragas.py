
import asyncio
import json
from pathlib import Path

from langchain_ollama import ChatOllama
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness


RAIZ = Path(__file__).resolve().parents[1]
PASTA_RESULTADOS = RAIZ / "evals" / "resultados"

ARQUIVO = PASTA_RESULTADOS / "ragas_prompt_v2.json"

IDS_DIAGNOSTICO = {"rag_03", "rag_04"}

MODELO_AVALIADOR = "llama3:latest"
OLLAMA_BASE_URL = "http://localhost:11434"


async def main():
    if not ARQUIVO.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {ARQUIVO}"
        )

    with ARQUIVO.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    llm_langchain = ChatOllama(
        model=MODELO_AVALIADOR,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
        num_predict=1024,
    )

    llm_avaliador = LangchainLLMWrapper(llm_langchain)
    metrica = Faithfulness(llm=llm_avaliador)

    resultados = dados.get("resultados", [])

    for item in resultados:
        identificador = item.get("id")

        if identificador not in IDS_DIAGNOSTICO:
            continue

        contextos = item.get("contextos_avaliados") or []

        if isinstance(contextos, str):
            contextos = [contextos]

        resposta = item.get("resposta_avaliada") or ""
        pergunta = item.get("pergunta") or ""

        if not resposta.strip() or not contextos:
            print(f"\n{identificador}: resposta/contexto ausente.")
            continue

        linha = {
            "user_input": pergunta,
            "response": resposta,
            "retrieved_contexts": contextos,
        }

        print("\n" + "=" * 70)
        print(f"TESTE: {identificador}")
        print("=" * 70)
        print("Pergunta:", pergunta)
        print("Nota original:", item.get("faithfulness"))

        print("\nExtraindo afirmações da resposta...")

        decomposicao = await metrica._create_statements(
            linha,
            callbacks=None,
        )

        afirmacoes = decomposicao.statements

        if not afirmacoes:
            print("O avaliador não extraiu nenhuma afirmação.")
            continue

        for indice, afirmacao in enumerate(afirmacoes, start=1):
            print(f"{indice}. {afirmacao}")

        print("\nJulgando as afirmações contra os contextos...")

        julgamento = await metrica._create_verdicts(
            linha,
            afirmacoes,
            callbacks=None,
        )

        for indice, resultado in enumerate(
            julgamento.statements,
            start=1,
        ):
            veredito = resultado.verdict

            if isinstance(veredito, bool):
                sustentada = veredito
            else:
                sustentada = veredito == 1

            print(f"\nAfirmação {indice}: {resultado.statement}")
            print(
                "Veredito:",
                "SUSTENTADA" if sustentada else "NÃO SUSTENTADA",
                f"(valor retornado: {veredito})",
            )
            print("Motivo:", resultado.reason)

        nota_recalculada = metrica._compute_score(julgamento)
        print("\nNota recalculada:", nota_recalculada)


if __name__ == "__main__":
    asyncio.run(main())
