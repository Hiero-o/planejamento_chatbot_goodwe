Relatório de Execução e Avaliação do RAG — GurAI | Sprint 04
1. Objetivo
Este relatório consolida os experimentos realizados no GurAI durante a Sprint 04, com foco na avaliação do pipeline RAG (Retrieval-Augmented Generation), na fidelidade das respostas ao contexto recuperado, na relevância das respostas, nas citações documentais e na capacidade de recusar perguntas sem suporte na base de conhecimento.

A análise utiliza os resultados previamente registrados nos arquivos JSON da pasta evals/resultados/, além dos relatórios técnicos e dos componentes de implementação presentes no repositório.
2. Base de conhecimento e configuração
A base documental utilizada nos experimentos é composta por três documentos técnicos da GoodWe:
Documento	Páginas
GW_HCA-G2_Datasheet-PT.pdf	2
GW_HCA-G2_User-Manual-PT.pdf	70
Mapa-MODBUS_HCA-G2.pdf	9
Total	81

O carregamento dos documentos é realizado por PyMuPDF, por meio de services/rag/document_loader.py. O processamento preserva metadados de documento e página para possibilitar a identificação das fontes utilizadas nas respostas.

O chunking utiliza RecursiveCharacterTextSplitter, com tamanho de 512 caracteres e sobreposição de 80 caracteres. Essa configuração busca manter trechos suficientemente pequenos para a recuperação semântica, preservando parte do conteúdo entre chunks consecutivos.

O armazenamento vetorial utiliza ChromaDB persistente, configurado em data/chroma_db/. O código atual seleciona embeddings locais utilizando nomic-embed-text, com vetores de 768 dimensões e prefixos específicos de consulta e documento.

A decisão de utilizar embeddings locais está relacionada às dificuldades encontradas na utilização do serviço Cloud para essa finalidade e à orientação discutida com o professor durante o desenvolvimento, que recomendou o uso do Ollama local diante das limitações de depender exclusivamente de serviços remotos.

O retriever utiliza uma estratégia híbrida, considerando até 24 candidatos antes de selecionar os quatro resultados finais para compor o contexto enviado ao modelo.

Na geração de respostas, a configuração registrada em src/chain/builder.py utiliza:
Parâmetro	Configuração
Modelo gerativo	Gemma 4, acessado pelo Ollama Cloud
temperature	0,3
top_p	0,9
num_predict	1.200
top_k do retriever	4
candidate_k do retriever	24

O top_k de recuperação é diferente do parâmetro top_k de geração do modelo. O código atual não define explicitamente este último. O limite de geração também é diferente do limite de 1.000 tokens utilizado na memória conversacional.
3. Metodologia de avaliação
O conjunto documental de avaliação contém dez perguntas fixas, registradas em evals/resultados/rag_evals_set.json: seis perguntas respondíveis com base nos documentos e quatro perguntas cuja informação não está disponível na base.

A avaliação automática utiliza o RAGAS 0.4.3, com o modelo llama3:latest e embeddings nomic-embed-text locais para o cálculo da relevância. As avaliações principais de Faithfulness e Answer Relevancy consideram exclusivamente as seis perguntas respondíveis.

As quatro perguntas não respondíveis são analisadas manualmente, pois uma recusa correta não deve ser penalizada por não fornecer uma resposta factual que a documentação não sustenta.

Também foi realizada uma verificação das citações, conferindo se o documento e a página indicados na resposta aparecem nos contextos recuperados. Essa verificação não comprova, isoladamente, a veracidade de todas as afirmações presentes na resposta.
4. Resultados da avaliação RAGAS
Os arquivos ragas_prompt_v2_respondiveis.json, ragas_prompt_v3_respondiveis.json e comparacao_ragas_respondiveis.json contêm os resultados utilizados para a comparação principal entre as versões v2 e v3.
Métrica	Prompt v2	Prompt v3	Variação
Faithfulness	0,9167	0,9667	+0,0500
Answer Relevancy	0,6762	0,6757	−0,0005

A versão v3 apresentou aumento de 0,05 em Faithfulness, equivalente a cinco pontos percentuais na escala da métrica. Esse resultado indica maior fidelidade média ao contexto recuperado nesse conjunto específico.

Por outro lado, Answer Relevancy permaneceu praticamente estável, com variação negativa de aproximadamente 0,0005. Portanto, os dados não demonstram melhora relevante da pertinência média das respostas nessa comparação.

A evolução observada é positiva para fidelidade, mas não permite concluir que a versão v3 seja superior em todos os aspectos ou para qualquer pergunta. A amostra é pequena e a avaliação depende de um modelo julgador.
5. Verificação das citações e das recusas
A verificação das referências apresentou os seguintes resultados:
Indicador	Prompt v2	Prompt v3
Respostas documentais com citações	6/6	6/6
Citações verificadas	10	11
Citações presentes nos contextos recuperados	10/10	11/11
Precisão de presença das citações	100%	100%
Recusas consideradas corretas	4/4	4/4

Os resultados indicam que todas as citações verificadas apontavam para documentos e páginas presentes nos contextos recuperados.

Entretanto, a métrica utilizada verifica a presença da referência, não a sustentação semântica integral de cada afirmação. Assim, os valores de 100% devem ser interpretados como precisão de presença das citações verificadas, e não como garantia absoluta de correção factual.

As quatro perguntas não respondíveis também receberam avaliação manual positiva nas duas versões. O sistema recusou fornecer informações ausentes da documentação, incluindo especificações desconhecidas de equipamentos e códigos de erro não documentados.
6. Iterações e ganho mensurável
Além da avaliação RAGAS, o projeto contém uma avaliação manual de duas iterações, registrada em evals/resultados/resumo_avaliacao_manual.json.

A rubrica utiliza notas entre 0 e 1, atribuídas após a inspeção das respostas e dos contextos recuperados.
Métrica	Iteração 1	Iteração 2	Ganho
Faithfulness	0,875	1,000	+0,125
Answer Relevancy	0,875	1,000	+0,125

Cada iteração contempla oito casos. O ganho foi de 12,5 pontos percentuais em ambas as métricas.

A principal correção documentada envolveu um falso bloqueio relacionado à pergunta sobre o código de erro 999999. Na primeira avaliação, o sistema apresentou uma recusa inadequada para o comportamento esperado naquele caso; após o ajuste, passou a produzir uma abstenção apropriada diante da ausência de informação documentada.

Esse resultado demonstra uma melhoria observada no comportamento do guardrail e na adequação da resposta. Contudo, ele não comprova, isoladamente, uma melhoria da recuperação vetorial ou da qualidade do prompt.

Há ainda uma avaliação manual posterior, com dez perguntas, na qual v2 e v3 obtiveram médias de 1,0 nas duas rubricas após a correção do ranking do retriever. Essa comparação empatada não deve ser utilizada para atribuir um ganho exclusivo à versão v3.
7. Comparação complementar entre modelos
O projeto também contém um experimento histórico da Sprint 03, com 39 testes para cada modelo: gpt-oss:120b e gemma4:31b-cloud.

Esse experimento é complementar à avaliação do RAG da Sprint 04 e não deve ser apresentado como se fosse uma execução RAGAS.
Métrica	GPT-OSS 120B	Gemma 4 31B Cloud
Testes registrados	39	39
Testes aprovados	37	39
Testes reprovados	2	0
Chamadas efetivas ao modelo	22	23
Média de tokens de entrada por chamada medida	2.905,41	4.054,48
Média de tokens de saída por chamada medida	183,91	58,35
Média de tokens totais por chamada medida	3.089,32	4.112,83
Latência média por teste	1,108 s	1,795 s

O GPT-OSS apresentou menor média de tokens totais e menor latência. Já o Gemma apresentou menor média de tokens de saída e concluiu os 39 testes sem reprovações registradas.

As duas falhas do GPT-OSS foram relacionadas à incompatibilidade de campos no Structured Output e à geração de orientações operacionais que ultrapassavam o comportamento de segurança esperado.

Os resultados demonstram um compromisso entre latência, consumo de contexto, extensão das respostas e aderência aos testes funcionais.
8. Limitações e interpretação final
Os experimentos disponíveis apresentam algumas limitações:
- O conjunto principal do RAG contém apenas dez perguntas, das quais seis são avaliadas automaticamente pelas métricas RAGAS.
- O modelo local utilizado como julgador pode cometer erros de avaliação.
- As recusas foram avaliadas manualmente, não constituindo métricas automáticas do RAGAS.
- A verificação de citações comprova a presença do documento e da página no contexto recuperado, mas não a sustentação de todas as afirmações.
- Os resultados demonstram ganhos em conjuntos específicos e não garantem generalização para perguntas não avaliadas.
- A geração de embeddings utiliza Ollama local, em vez da configuração Cloud mencionada no enunciado, por decisão técnica adotada diante das dificuldades encontradas.
Conclui-se que o GurAI possui evidências de evolução do pipeline RAG, com persistência vetorial, recuperação híbrida, citações documentais e avaliação quantitativa e manual. A comparação RAGAS identificou aumento de Faithfulness entre v2 e v3, enquanto a avaliação manual registrou ganho de 0,125 nas duas métricas entre as iterações. A pertinência permaneceu praticamente estável na comparação RAGAS, indicando que ainda há espaço para melhorar a qualidade das respostas.

Os resultados devem ser interpretados como evidências experimentais do comportamento do sistema nos conjuntos avaliados, e não como garantia de desempenho universal.