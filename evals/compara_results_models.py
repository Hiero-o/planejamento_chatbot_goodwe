import json
from pathlib import Path

def load_results(nome_arquivo):
    caminho = Path(__file__).parent / nome_arquivo

    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def calcular_metricas(dados):
    testes = dados["testes"]

    latencias = []
    input_tokens = []
    output_tokens = []
    total_tokens = []

    for teste in testes:
        latencias.append(teste["latencia_seg"])

        if "total_tokens" in teste and teste["total_tokens"] > 0:
            input_tokens.append(teste["input_tokens"])
            output_tokens.append(teste["output_tokens"])
            total_tokens.append(teste["total_tokens"])

    return {
        "quantidade_testes": len(teste),
        "latencia_media": sum(latencias) / len(latencias),
        "input_tokens_medio": (
            sum(input_tokens) / len(input_tokens)
            if input_tokens else 0
        ),

        "input_tokens_medio": (
            sum(input_tokens) / len(input_tokens)
            if input_tokens else 0
        ),

        "output_tokens_medio": (
            sum(output_tokens) / len(output_tokens)
            if output_tokens else 0
        ),

        "total_tokens_medio": (
            sum(total_tokens) / len(total_tokens)
            if total_tokens else 0
        ),

        "testes_com_modelo": len(total_tokens)
    }


def save_summary(gpt, gemma, output_diff, total_diff, latency_diff):
    caminho = Path(__file__).parent / "comparacao_modelos_sumario.json"

    dados = {
        "gpt-oss:120b": gpt,
        "gemma:31b-cloud": gemma,
        "diferencas_percentuais": {
            "output_tokens": output_diff,
            "total_tokens": total_diff,
            "latency_tokens": latency_diff
        }
    }

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)

    print(f"\n Resumo salvo em {caminho}")


def diferenca_percentual(valor_a, valor_b):
    if valor_a == 0:
        return 0

    return ((valor_a - valor_b) / valor_a) * 100


def mostrar_comparacao(gpt, gemma):
    print("\n" + "=" * 60)
    print("COMPARAÇÃO DE MODELOS")
    print("=" * 60)

    print(
        f"\n{'Métrica':<25}"
        f"{'GPT-OSS':>15}"
        f"{'Gemma 4':>15}"
    )
    print("-" * 60)

    print(
        f"{'Testes':<25}"
        f"{gpt['quantidade_testes']:>15}"
        f"{gemma['quantidade_testes']:>15}"
    )

    print(
        f"{'Testes com modelo':<25}"
        f"{gpt['testes_com_modelo']:>15}"
        f"{gemma['testes_com_modelo']:>15}"
    )

    print(
        f"{'Input tokens (média)':<25}"
        f"{gpt['input_tokens_medio']:>15.2f}"
        f"{gemma['input_tokens_medio']:>15.2f}"
    )

    print(
        f"{'Output tokens (média)':<25}"
        f"{gpt['output_tokens_medio']:>15.2f}"
        f"{gemma['output_tokens_medio']:>15.2f}"
    )

    print(
        f"{'Total tokens (média)':<25}"
        f"{gpt['total_tokens_medio']:>15.2f}"
        f"{gemma['total_tokens_medio']:>15.2f}"
    )

    print(
        f"{'Latência média (s)':<25}"
        f"{gpt['latencia_media']:>15.2f}"
        f"{gemma['latencia_media']:>15.2f}"
    )

    print("\n" + "-" * 60)
    print("DIFERENÇAS")
    print("-" * 60)

    output_diff = diferenca_percentual(
        gpt["output_tokens_medio"],
        gemma["output_tokens_medio"]
    )

    total_diff = diferenca_percentual(
        gpt["total_tokens_medio"],
        gemma["total_tokens_medio"]
    )

    latency_diff = diferenca_percentual(
        gpt["latencia_media"],
        gemma["latencia_media"]
    )

    print(
        f"Gemma 4 utiliza {output_diff:.2f}% menos output tokens."
    )

    print(
        f"Gemma 4 utiliza {total_diff:.2f}% menos tokens totais."
    )

    print(
        f"Gemma 4 apresenta {latency_diff:.2f}% menor latência."
    )

    save_summary(gpt, gemma, output_diff, total_diff, latency_diff)


if __name__ == "__main__":

    gpt_results = load_results("gpt_oss_results.json")
    gemma_results = load_results("gemma4_results.json")

    gpt_metricas = calcular_metricas(gpt_results)
    gemma_metricas = calcular_metricas(gemma_results)

    mostrar_comparacao(
        gpt_metricas,
        gemma_metricas
    )