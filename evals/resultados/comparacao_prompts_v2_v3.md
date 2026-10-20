# Comparação manual de prompts — GurAI

## Metodologia

Foram comparadas as respostas dos prompts v2 e v3 usando os mesmos dez casos de teste.
A avaliação é manual e baseada nas respostas geradas, nas respostas esperadas e nos contextos recuperados.

As notas variam entre 0 e 1.
Este resultado é um fallback manual e não uma execução do RAGAS.

## Médias por versão

| Versão | Testes | Faithfulness | Answer relevancy |
|---|---:|---:|---:|
| v2 | 10 | 0.950 | 0.950 |
| v3 | 10 | 0.950 | 0.950 |

## Comparação antes/depois

- Variação em faithfulness: +0.000 (+0.0 pontos percentuais).
- Variação em answer relevancy: +0.000 (+0.0 pontos percentuais).

## Notas por teste

| Teste | Faithfulness v2 | Relevância v2 | Faithfulness v3 | Relevância v3 |
|---|---:|---:|---:|---:|
| rag_01 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_02 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_03 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_04 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_05 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_06 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_07 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_08 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_09 | 0.5 | 0.5 | 0.5 | 0.5 |
| rag_10 | 1.0 | 1.0 | 1.0 | 1.0 |

## Interpretação

As versões mantiveram comportamento semelhante nos casos avaliados. O teste rag_09 recebeu pontuação parcial porque o contexto não incluiu a explicação documental sobre a limitação de carregamento pelo OBC.

O resultado de rag_09 evidencia uma limitação do pipeline de recuperação e não permite atribuir a falha unicamente ao prompt.

As médias não demonstram, por si só, superioridade de uma versão. O conjunto é pequeno, fixo e avaliado manualmente.
Os resultados devem ser interpretados como evidência preliminar, não como garantia de desempenho geral.
