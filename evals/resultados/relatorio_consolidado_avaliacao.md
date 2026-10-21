# Avaliação consolidada do RAG GurAI — Sprint 04

## 1. Escopo e metodologia

O conjunto de avaliação contém dez perguntas fixas: seis respondíveis e quatro não respondíveis. Nenhuma pergunta foi excluída por ter obtido uma nota baixa.

As seis perguntas respondíveis são avaliadas com RAGAS 0.4.3 usando o Llama 3 local como juiz e nomic-embed-text local na métrica de relevância. As quatro recusas são revisadas manualmente, pois uma recusa correta não deve ser tratada simplesmente como uma resposta factual comum.

As referências são verificadas separadamente pela presença do documento e da página citados nos contextos recuperados.

## 2. Resultados principais: perguntas respondíveis

| Métrica | v2 | v3 | Diferença v3 - v2 |
|---|---:|---:|---:|
| Faithfulness | 0.917 | 0.967 | 0.050 |
| Answer Relevancy | 0.676 | 0.676 | -0.001 |

## 3. Resultados por pergunta

| ID | Faithfulness v2 | Faithfulness v3 | Relevância v2 | Relevância v3 |
|---|---:|---:|---:|---:|
| rag_01 | 1.000 | 1.000 | 0.786 | 0.790 |
| rag_02 | 1.000 | 1.000 | 0.786 | 0.790 |
| rag_03 | 1.000 | 1.000 | 0.609 | 0.608 |
| rag_04 | 0.500 | 1.000 | 0.674 | 0.709 |
| rag_05 | 1.000 | 1.000 | 0.609 | 0.629 |
| rag_09 | 1.000 | 0.800 | 0.592 | 0.528 |

## 4. Verificação de citações

| Resultado | v2 | v3 |
|---|---:|---:|
| Precisão micro das citações | 1.000 | 1.000 |
| Precisão média por resposta | 1.000 | 1.000 |

A verificação confirma somente se o par documento/página está presente nos contextos recuperados; não valida semanticamente todo o conteúdo da resposta.

## 5. Perguntas não respondíveis e recusas

| ID | Avaliação v2 | Avaliação v3 |
|---|---|---|
| rag_06 | Correta | Correta |
| rag_07 | Correta | Correta |
| rag_08 | Correta | Correta |
| rag_10 | Correta | Correta |

- v2: 4/4 recusas corretas.
- v3: 4/4 recusas corretas.

As notas das recusas são avaliações manuais, não métricas calculadas pelo RAGAS.

## 6. Rodada exploratória com os dez testes

| Métrica | v2 | v3 |
|---|---:|---:|
| Faithfulness média | 0.680 | 0.537 |
| Answer Relevancy média | 0.408 | 0.410 |

Esta rodada é mantida para transparência, mas não é a comparação principal: ela combina perguntas factuais e perguntas em que a resposta correta é uma recusa. Além disso, uma avaliação individual da fidelidade da v3 falhou em uma execução exploratória anterior.

## 7. Interpretação

Neste conjunto pequeno, a v3 obteve Faithfulness média maior nas seis perguntas respondíveis, enquanto Answer Relevancy permaneceu praticamente empatada. Os quatro casos de recusa foram considerados corretos nas duas versões pela revisão manual.

Esses resultados não provam superioridade geral da v3. O avaliador é um modelo local, pode cometer erros e a amostra é pequena. São necessários mais testes para avaliar generalização e consistência.

## 8. Limitações

- O conjunto contém dez perguntas e é pequeno.
- O Llama 3 usado como avaliador pode cometer erros.
- A presença de uma citação no contexto não comprova automaticamente todas as afirmações da resposta.
- A revisão das recusas é manual e não constitui uma métrica automática RAGAS.
- A comparação não prova generalização para perguntas fora do conjunto avaliado.
