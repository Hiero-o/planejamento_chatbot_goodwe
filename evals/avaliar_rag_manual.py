
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Garante que a raiz do projeto esteja no caminho de importação.
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from services.question_processor import process_question
from src.rag.context_builder import build_documentation_context


ARQUIVO_TESTES = RAIZ / "evals" / "rag_evals_set.json"


def extrair_fontes(contexto):
    """Extrai os nomes dos documentos e as páginas do contexto."""
    if not contexto:
        return []

    padrao = re.compile(
        r"Documento:\s*(.*?)\s*\n"
        r"Página:\s*(\d+)",
        re.IGNORECASE,
    )

    fontes = []
    fontes_vistas = set()

    for documento, pagina in padrao.findall(contexto):
        fonte = {
            "documento": documento.strip(),
            "pagina": int(pagina),
        }

        chave = (fonte["documento"], fonte["pagina"])

        if chave not in fontes_vistas:
            fontes.append(fonte)
            fontes_vistas.add(chave)

    return fontes


def carregar_testes():
    """Carrega e valida o conjunto fixo de perguntas."""
    if not ARQUIVO_TESTES.exists():
        raise FileNotFoundError(
            f"Arquivo de testes não encontrado: {ARQUIVO_TESTES}"
        )

    with ARQUIVO_TESTES.open("r", encoding="utf-8") as arquivo:
        testes = json.load(arquivo)

    if not isinstance(testes, list) or not testes:
        raise ValueError("O conjunto de avaliação está vazio ou inválido.")

    for teste in testes:
        for campo in ("id", "tipo", "pergunta", "resposta_esperada"):
            if campo not in teste:
                raise ValueError(
                    f"Teste sem o campo obrigatório '{campo}': {teste}"
                )

    return testes


def avaliar_teste(teste):
    """Executa a recuperação documental e a resposta do GurAI."""
    pergunta = teste["pergunta"]
    identificador = teste["id"]

    resultado = {
        **teste,
        "contexto_recuperado": None,
        "fontes_recuperadas": [],
        "resposta_gerada": None,
        "erro_contexto": None,
        "erro_resposta": None,
        "avaliacao_manual": {
            "faithfulness": None,
            "answer_relevancy": None,
            "justificativa_faithfulness": "",
            "justificativa_answer_relevancy": "",
        },
    }

    print(f"\n{'=' * 70}")
    print(f"Teste: {identificador}")
    print(f"Pergunta: {pergunta}")

    # Recupera o contexto para que possamos inspecionar
    # as evidências utilizadas na avaliação.
    try:
        contexto = build_documentation_context(pergunta)

        resultado["contexto_recuperado"] = contexto
        resultado["fontes_recuperadas"] = extrair_fontes(contexto)

        if contexto:
            print(
                "Contexto recuperado:",
                len(contexto),
                "caracteres",
            )
            print(
                "Quantidade de referências encontradas:",
                len(resultado["fontes_recuperadas"]),
            )
        else:
            print("Contexto recuperado: nenhum trecho.")

    except Exception as erro:
        resultado["erro_contexto"] = (
            f"{type(erro).__name__}: {erro}"
        )
        print("Erro ao recuperar contexto:", resultado["erro_contexto"])

    # Cada pergunta recebe uma sessão independente para reduzir
    # a influência do histórico de outras perguntas.
    try:
        resposta = process_question(
            question=pergunta,
            session_id=f"sprint04_eval_{identificador}",
        )

        if not isinstance(resposta, str):
            resposta = str(resposta)

        resultado["resposta_gerada"] = resposta.strip()
        print("Resposta gerada:")
        print(resultado["resposta_gerada"])

    except Exception as erro:
        resultado["erro_resposta"] = (
            f"{type(erro).__name__}: {erro}"
        )
        print("Erro ao gerar resposta:", resultado["erro_resposta"])

    return resultado


def main():
    parser = argparse.ArgumentParser(
        description="Executa a avaliação documental do GurAI."
    )
    parser.add_argument(
        "--saida",
        default="evals/resultados_rag_iteracao_1.json",
        help="Caminho do arquivo JSON que armazenará os resultados.",
    )
    args = parser.parse_args()

    testes = carregar_testes()
    resultados = []

    print("=" * 70)
    print("AVALIAÇÃO MANUAL DO RAG — GURAI")
    print("=" * 70)
    print(f"Quantidade de perguntas: {len(testes)}")

    for indice, teste in enumerate(testes, start=1):
        print(f"\nProgresso: {indice}/{len(testes)}")
        resultados.append(avaliar_teste(teste))

    caminho_saida = Path(args.saida)

    if not caminho_saida.is_absolute():
        caminho_saida = RAIZ / caminho_saida

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    documento_saida = {
        "experimento": "Sprint 04 — avaliação manual do RAG",
        "iteracao": 1,
        "data_execucao": datetime.now().astimezone().isoformat(),
        "quantidade_testes": len(resultados),
        "criterio_avaliacao": (
            "Notas manuais de 0 a 1, justificadas com base "
            "na resposta e no contexto recuperado."
        ),
        "resultados": resultados,
    }

    with caminho_saida.open("w", encoding="utf-8") as arquivo:
        json.dump(
            documento_saida,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )

    erros = sum(
        item["erro_resposta"] is not None
        or item["erro_contexto"] is not None
        for item in resultados
    )

    print("\n" + "=" * 70)
    print("EXECUÇÃO CONCLUÍDA")
    print("=" * 70)
    print(f"Perguntas executadas: {len(resultados)}")
    print(f"Testes com erros técnicos: {erros}")
    print(f"Arquivo salvo em: {caminho_saida}")
    print(
        "As notas de faithfulness e answer_relevancy "
        "permanecem pendentes de avaliação."
    )


if __name__ == "__main__":
    main()
