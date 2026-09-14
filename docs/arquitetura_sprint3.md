# Arquitetura — Sprint 03

## 1. Objetivo

Documentar as mudanças arquiteturais do GruAI para a sprint 3, assim como as decisoes para o refatoramento.

---

## 2. Estado inicial

O `question_processor.py` concentrava diversas responsabilidades:

- normalização da pergunta;
- detecção de intents;
- tratamento hardcoded de erros Modbus;
- consultas de dados dinâmicos dos carregadores;
- busca de conhecimento documental;
- montagem de contexto e instruções para o LLM;
- gerenciamento de memória;
- chamada do modelo.

Isso acaba limitando a evolução do sistema.

---

## 3. Arquitetura planejada

O sistema terá três responsabilidades principais:

### 3.1 Dados dinâmicos

Responsável por consultar informações atuais, como:

- status dos carregadores;
- potência;
- energia;
- carregadores ativos;
- carregadores disponíveis.

### 3.2 Conhecimento técnico

Responsável pelas informações presentes na documentação, incluindo:

- manuais;
- documentação técnica;
- dados Modbus.

A recuperação desse conhecimento será realizada pelo sistema de RAG.

### 3.3 Conversação

Responsável por:

- prompt;
- memória;
- processamento da conversa;
- chamada do LLM;
- geração da resposta.

Essa camada será migrada para LangChain/LCEL conforme o desenvolvimento da Sprint 03.

---

## 4. Decisões de refatoração

| Componente atual | Decisão | Destino |
|---|---|---|
| Normalização | Manter | question_processor.py |
| detect_intent() | Simplificar | intents.py |
| Erros 0x0001–0x0004 hardcoded | Remover | RAG/Modbus |
| Consultas de carregadores | Mover | dynamic_queries.py |
| Consultas agregadas | Mover | dynamic_queries.py |
| search_conhecimento() | Substituir | RAG |
| Prompt hardcoded no processor | Substituir | Prompt versionado |
| Bloqueio pergunta_tecnica | Remover/reformular | Grounding/guardrails |
| Memory atual | Substituir | LangChain |
| ask_model() | Substituir | LCEL |

---

## 5. Princípios

### Separação de responsabilidades

O `question_processor.py` deverá atuar principalmente como
orquestrador, para não concentrar regras específicas de conhecimento,
dados ou geração de respostas.

### Conhecimento fora do código

Informações técnicas não devem ser mantidas como respostas completamente hardcoded
no código quando puderem ser obtidas da documentação. (Isso se tornará legado, visto que o RAG ainda não está totalmente finalizado e implementado.)

### Grounding sem bloqueio excessivo

O sistema deve reduzir alucinações sem impedir desnecessariamente o
modelo de responder quando houver conhecimento suficiente.

### Mudanças incrementais

A refatoração será realizada em pequenas etapas, validando o sistema
após cada alteração significativa.

---

## 6. Histórico de mudanças

| Data | Mudança | Status |
|---|---|---|
| — | Criação do baseline dos Evals | Em andamento |
| — | Versionamento do prompt como v1 | Concluído |
| — | Mapeamento de responsabilidades do `question_processor.py` | Concluído |
| — | Separação de dados dinâmicos | Pendente |
| — | Integração do RAG | Pendente |
| — | Migração para LCEL | Pendente |
| — | Migração da memória | Pendente |
| — | Structured Output | Pendente |