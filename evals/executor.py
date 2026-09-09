# ESSE CODIGO TESTARÁ TODAS AS PERGUNTAS DO EVALS_SET.JSON NO MODELO DO GURAI, ARMAZENANDO TUDO DE FORMA ESTRUTURADA NO BASELINE_RESULTS.JSON.

import json
import time
from pathlib import Path

from chatbot.memory import Memory
from chatbot.prompt_loader import load_prompt
from services.question_processor import process_question

def load_eval():
    caminho = Path(__file__).parent / "evals_set.json"

    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def run_memory_test(teste):
    system_prompt = load_prompt()
    memory = Memory(system_prompt)

    inicio = time.perf_counter()

    respostas = []

    for pergunta in teste["turnos"]:
        resposta = process_question(pergunta, memory)

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
    system_prompt = load_prompt()
    memory = Memory(system_prompt)
    pergunta = testes["pergunta"]
    inicio = time.perf_counter()
    resposta = process_question(pergunta, memory)
    fim = time.perf_counter()
    latencia = fim - inicio


    return {
        "id": testes["id"],
        "pergunta": pergunta,
        "resposta": resposta,
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

        print(f"Resposta: {resultado["resposta"]}")
        print(f"Latencia: {resultado["latencia_seg"]:.2f} segundos")
        print(f"\nQuantidade de execuções: {len(resultados)}\n")


   