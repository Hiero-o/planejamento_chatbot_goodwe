# Avaliação manual do RAG — comparação v2 × v3

## Metodologia

Foram avaliadas manualmente as respostas de dez perguntas documentais para cada versão do prompt, depois da correção do ranking do retriever.

As notas variam de 0 a 1:

- 1,0: resposta sustentada pelo contexto e adequada à pergunta.
- 0,5: suporte ou atendimento parcial.
- 0,0: afirmação não sustentada ou resposta inadequada.

As métricas representam avaliação manual, e não scores calculados automaticamente pelo RAGAS.

## Resultado por versão

| Prompt | Testes | Faithfulness | Answer relevancy |
|---|---:|---:|---:|
| v2 | 10 | 1.000 | 1.000 |
| v3 | 10 | 1.000 | 1.000 |

## Comparação v2 × v3

- Variação em faithfulness: +0.000.
- Variação em answer relevancy: +0.000.

As versões empataram nas métricas deste conjunto de avaliação. Não foi demonstrada superioridade da v3.

## Evolução do retriever

Na avaliação preliminar, antes do ajuste do ranking, o rag_09 recebeu nota parcial porque o contexto final não continha a explicação sobre a limitação pelo OBC.
Após a alteração do ranking, os trechos do manual na página 14 passaram a aparecer entre os primeiros resultados e as respostas passaram a explicar a influência do OBC com citações documentais.

A média manual preliminar anterior era 0,950 em ambas as métricas. A média após a correção ficou em 1,000, uma diferença de +0,050. Esse resultado está associado à correção do retriever, não a uma vantagem isolada da v3.

## Resultados por pergunta

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
| rag_09 | 1.0 | 1.0 | 1.0 | 1.0 |
| rag_10 | 1.0 | 1.0 | 1.0 | 1.0 |

## Limitações

A avaliação utiliza dez perguntas e uma rubrica manual. As médias não garantem desempenho geral para perguntas fora desse conjunto.
A avaliação do prompt e a avaliação do retriever devem permanecer separadas para não atribuir a uma mudança um ganho produzido por outra.
Neste projeto, os embeddings são gerados localmente pelo Ollama usando o modelo nomic-embed-text, com RAG_EMBEDDING_PROVIDER=local. Essa escolha é intencional e está alinhada à preferência do professor. O provedor de embeddings é independente do provedor do modelo generativo: o GurAI pode utilizar o gemma4:31b-cloud para gerar respostas e manter a geração de embeddings na máquina local.