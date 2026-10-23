# Histórico de versões do System Prompt

| Versão | Alteração | Motivo | Resultado |
|---|---|---|---|
| v1 | Prompt original das Sprints 1/2 | Estabelecer o comportamento inicial do GurAI | 1.724 tokens |
| v2 | Reorganização das instruções utilizando XML tags | Melhorar a organização e a estrutura do contexto | 3.230 tokens (+1.506 vs. v1); utilizada na Sprint 03 |
| v3 | Explicitação das regras de grounding documental, citações por documento e página, validação de evidências, proteção contra prompt injection em documentos e tratamento das sessões pessoais autenticadas | Reduzir respostas sem sustentação documental, evitar especificações inventadas e reforçar a segurança | 3.605 tokens (+375 vs. v2); Faithfulness: 0,9167 → 0,9667; Answer Relevancy: 0,6762 → 0,6757 |

## Observações sobre a avaliação

A contagem de tokens foi realizada utilizando tiktoken com o encoder cl100k_base, mantendo o mesmo método para as três versões.

Na comparação RAGAS entre v2 e v3, realizada com seis perguntas respondíveis, a Faithfulness aumentou 0,0500, enquanto a Answer Relevancy apresentou variação de -0,0005, permanecendo praticamente estável.

A verificação de presença das citações registrou 10/10 referências na v2 e 11/11 na v3 presentes nos contextos recuperados. As recusas foram consideradas corretas em 4/4 casos em ambas as versões.

Esses resultados correspondem aos experimentos registrados e não garantem que todas as afirmações estejam semanticamente sustentadas pelas fontes em qualquer cenário.
