# Relatório de avaliação manual do RAG — GurAI

## Metodologia

Foi aplicado o mesmo conjunto de perguntas documentais nas duas execuções.
As notas variam de 0 a 1 e foram atribuídas manualmente após inspeção das respostas e dos contextos recuperados.

- Faithfulness: fidelidade das afirmações ao contexto.
- Answer relevancy: pertinência da resposta à pergunta.
- A qualidade das citações deve também ser verificada separadamente.

Esta avaliação é um fallback manual, não uma execução do RAGAS.

## Resultados gerais

| Iteração | Faithfulness média | Answer relevancy média |
|---|---:|---:|
| 1 | 0.875 | 0.875 |
| 2 | 1.000 | 1.000 |

## Comparação antes e depois

- Ganho em faithfulness: +0.125 (+12.5 pontos percentuais).
- Ganho em answer_relevancy: +0.125 (+12.5 pontos percentuais).

## Pontuação por pergunta

| Teste | Faithfulness I1 | Relevância I1 | Faithfulness I2 | Relevância I2 |
|---|---:|---:|---:|---:|
| rag_01 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_02 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_03 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_04 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_05 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_06 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_07 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_08 | 0.0 | 0.0 | 1.0 | 1.0 |

## Interpretação

A principal mudança avaliada foi a correção do falso bloqueio da pergunta sobre o código de erro 999999. A segunda execução passou a responder com uma abstenção apropriada.

O ganho está relacionado ao comportamento do guardrail e à pertinência da resposta. Ele não demonstra, isoladamente, melhoria na recuperação documental ou no prompt RAG.

As versões e os parâmetros do pipeline precisam ser registrados separadamente para completar a análise de evolução exigida pela Sprint 04.
