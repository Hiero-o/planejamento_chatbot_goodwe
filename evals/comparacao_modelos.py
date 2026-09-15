# Este código testa as perguntas do evals_set.json no GurAI
# refatorado para o Sprint 3 e armazena os resultados
# de forma estruturada no sprint3_results.json.

import json
import time
from pathlib import Path

from services.question_processor import process_question

def load_eval():
    caminho = Path(__file__).parent / "evals_set.json"

    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def save_results(resultados):
    caminho = Path(__file__).parent / "sprint3_results.json"

    dados = {
        "tipo": "sprint3",
        "testes": resultados
    }

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)

    print(f"\n Resultados salvos em: {caminho}")


def run_memory_test(teste):
    session_id = f"eval_memory_{teste['id']}"

    inicio = time.perf_counter()

    respostas = []

    for pergunta in teste["turnos"]:
        resposta = process_question(
            pergunta,
            session_id
        )

        respostas.append({
            "pergunta": pergunta,
            "resposta": resposta
        })

    fim = time.perf_counter()

    return {
        "id": teste["id"],
        "categoria": teste["categoria"],
        "turnos": respostas,
        "criterio": teste["criterio"],
        "latencia_seg": fim - inicio
    }


def test(testes):
    pergunta = testes["pergunta"]

    session_id = f"eval_{testes['id']}"

    inicio = time.perf_counter()

    resultado = process_question(
        pergunta,
        session_id,
        retornar_metricas=True
    )

    resultado = process_question(
    pergunta,
    "eval_session",
    retornar_metricas=True
    )

    print("TIPO DO RESULTADO:", type(resultado))
    print("RESULTADO:", resultado)

    fim = time.perf_counter()
    latencia = fim - inicio

    if isinstance(resultado, dict):
        input_tokens = resultado["input_tokens"]
        output_tokens = resultado["output_tokens"]
        total_tokens = input_tokens + output_tokens
        resposta = resultado["resposta"]

    else:
        input_tokens = 0
        output_tokens = 0
        total_tokens = 0
        resposta = resultado

    return {
        "id": testes["id"],
        "pergunta": pergunta,
        "resposta": resposta,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "latencia_seg": latencia
    }

if __name__ == "__main__":

    testes = load_eval()

    resultados = []

    for teste in testes:
        print(f"\nExecutando Teste: {teste["id"]}")

        if teste["categoria"] == "memoria":
            print("Teste de memoria detectado.")
            print(f"Turnos: {len(teste['turnos'])}")

            resultado = run_memory_test(teste)

            resultados.append(resultado)

            for turno in resultado["turnos"]:
                print(f"\n Pergunta: {turno['pergunta']}")
                print(f" Resposta: {turno['resposta']}")

            print(
                f"\nLatencia Total: "
                f"{resultado['latencia_seg']:.2f} segundos"
            )

            continue

        print(f"Pergunta: {teste["pergunta"]}")

        resultado = test(teste)

        resultados.append(resultado)

        print(f"Resposta: {resultado['resposta']}")
        print(f"Input tokens: {resultado['input_tokens']}")
        print(f"Output tokens: {resultado['output_tokens']}")
        print(f"Total tokens: {resultado['total_tokens']}")
        print(f"Latência: {resultado['latencia_seg']:.2f} segundos")
        print(f"\nQuantidade de execuções: {len(resultados)}\n")

        save_results(resultados)
