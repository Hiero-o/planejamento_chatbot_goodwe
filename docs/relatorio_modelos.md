# Relatório de Uso de Modelos e Parâmetros — Sprint 03

## 1. Objetivo

Este documento registra os modelos utilizados pelo GurAI na Sprint 03, os principais parâmetros de geração e os resultados obtidos no conjunto de avaliação utilizado para comparação.

A comparação foi realizada sobre o mesmo conjunto de **39 testes**, utilizando a mesma versão do sistema e os mesmos parâmetros de geração para os dois modelos. O objetivo foi observar diferenças de comportamento em consumo de tokens, latência e aderência aos testes funcionais.

Os modelos avaliados foram:

- `gpt-oss:120b`
- `gemma4:31b-cloud`

O modelo atualmente utilizado pelo GurAI é o `gemma4:31b-cloud`.

## 2. Modelos utilizados

| Modelo | Provider / acesso | Uso |
|---|---|---|
| `gpt-oss:120b` | Ollama Cloud | Modelo utilizado para o comparativo da Sprint 03 |
| `gemma4:31b-cloud` | Ollama Cloud | Modelo atualmente utilizado pelo GurAI |

A arquitetura utiliza `ChatOllama` com acesso ao Ollama Cloud. Os dois modelos foram executados sobre o mesmo conjunto de 39 testes, mantendo a mesma configuração de geração, de modo a reduzir diferenças causadas por parâmetros experimentais.

## 3. Parâmetros de geração e memória

Os dois modelos foram executados com os mesmos parâmetros:

| Parâmetro | Valor | Finalidade |
|---|---:|---|
| `temperature` | `0.3` | Favorecer respostas mais consistentes e menos variáveis |
| `top_p` | `0.9` | Restringir a geração ao conjunto de tokens mais prováveis |
| `num_predict` | `1200` | Limitar a quantidade máxima de tokens gerados pela resposta |
| `max_token_limit` | `1000` | Limitar a quantidade de tokens mantidos no histórico da memória conversacional |

O `max_token_limit` pertence à memória conversacional e não ao mecanismo de geração do modelo. Já `num_predict` controla o limite de geração da resposta.

A configuração utilizada no `ChatOllama` foi:

```python
temperature=0.3,
top_p=0.9,
num_predict=1200
```

Para a memória conversacional:

```python
ConversationTokenBufferMemory(
    llm=llm,
    max_token_limit=1000,
    return_messages=True
)
```

## 4. Resultados quantitativos

Os resultados abaixo foram calculados a partir dos arquivos finais de avaliação dos dois modelos.

| Métrica | `gpt-oss:120b` | `gemma4:31b-cloud` |
|---|---:|---:|
| Testes avaliados | 39 | 39 |
| Testes aprovados | 37 | 39 |
| Testes reprovados | 2 | 0 |
| Testes com chamada efetiva ao modelo | 22 | 23 |
| Input tokens — média* | 2.905,41 | 4.054,48 |
| Output tokens — média* | 183,91 | 58,35 |
| Total tokens — média* | 3.089,32 | 4.112,83 |
| Latência média — todos os testes | 1,108 s | 1,795 s |

\* As médias de tokens consideram os testes que efetivamente possuem métricas de uso do modelo nos arquivos de resultado. Os testes determinísticos apresentam `0` tokens e não representam consumo de geração do LLM. O teste de memória também não registra tokens de entrada e saída no formato dos demais testes.

### Diferenças observadas

Considerando os resultados da execução:

- O `gemma4:31b-cloud` apresentou aproximadamente **68,27% menos tokens de saída** que o `gpt-oss:120b`.
- O `gemma4:31b-cloud` apresentou aproximadamente **39,55% mais tokens de entrada** que o `gpt-oss:120b`.
- O `gemma4:31b-cloud` apresentou aproximadamente **33,13% mais tokens totais** que o `gpt-oss:120b`.
- A latência média do `gemma4:31b-cloud` foi aproximadamente **62,01% maior** que a do `gpt-oss:120b`.
- O conjunto de avaliação registrou **39/39 testes aprovados para o `gemma4:31b-cloud`** e **37/39 para o `gpt-oss:120b`**.

Os dois testes reprovados do `gpt-oss:120b` ocorreram em `operacional_02`, devido à incompatibilidade de campo no Structured Output (`charger` em vez de `carregador`), e em `suporte_01`, em que a resposta apresentou instruções operacionais de diagnóstico mais amplas do que o comportamento de segurança esperado.

## 5. Interpretação dos resultados

A comparação demonstra diferenças relevantes entre os modelos no comportamento de geração.

O `gpt-oss:120b` apresentou menor média de tokens de entrada e menor média de tokens totais, além de menor latência média no conjunto completo. Em contrapartida, apresentou maior quantidade média de tokens de saída e duas falhas nos testes avaliados.

O `gemma4:31b-cloud` apresentou maior consumo médio de tokens de entrada e de tokens totais, além de maior latência média. Entretanto, apresentou menor quantidade média de tokens de saída e não apresentou reprovações nos 39 testes desta execução.

Esses resultados indicam um trade-off entre quantidade de contexto processado, tamanho das respostas, latência e aderência aos testes funcionais.

A análise também deve considerar que parte do sistema utiliza caminhos determinísticos que não chamam o LLM. Esses caminhos apresentam `0` tokens e latência de milissegundos, contribuindo para a média geral de latência sem representar processamento realizado pelo modelo.

## 6. Structured Output e comportamento observado

A comparação mostrou uma diferença importante na integração com Structured Output.

No teste `operacional_02`, o `gpt-oss:120b` retornou um objeto contendo o campo `charger`, enquanto o schema Pydantic utilizado pelo GurAI exige o campo `carregador`. A incompatibilidade provocou falha na validação e impediu a conclusão normal do teste.

O `gemma4:31b-cloud` concluiu o conjunto de avaliação sem ocorrência equivalente nos 39 testes.

Esse resultado demonstra que a comparação de modelos não deve considerar somente tokens e latência: a aderência ao schema e às regras definidas pelo sistema também é relevante.

## 7. Configuração de memória e limite de geração

A Sprint 03 utiliza dois mecanismos diferentes de controle de tokens:

```python
ConversationTokenBufferMemory(
    llm=llm,
    max_token_limit=1000,
    return_messages=True
)
```

O limite de `1000` tokens está relacionado ao histórico mantido pela memória conversacional.

Na geração dos modelos, a configuração atual utiliza:

```python
temperature=0.3,
top_p=0.9,
num_predict=1200
```

Dessa forma, o sistema estabelece separadamente um limite para o histórico conversacional e um limite para a quantidade de tokens gerados em uma resposta.

## 8. Context Engineering e impacto no prompt

A medição atual do contexto registra:

```text
System Prompt v1: 1724 tokens
System Prompt v2: 2715 tokens
Diferença: 991 tokens
```

A versão 2 do System Prompt utiliza organização estruturada por XML e reúne regras de escopo, segurança, prevenção de alucinação e utilização do contexto.

O aumento de 991 tokens representa maior quantidade de instruções presentes no contexto enviado ao modelo. Portanto, o consumo total de tokens deve ser interpretado em conjunto com a estratégia de Context Engineering adotada na Sprint 03.

## 9. Conclusão

A comparação realizada na Sprint 03 demonstra que os dois modelos apresentaram comportamentos distintos sob a mesma configuração de geração e sobre o mesmo conjunto de 39 testes.

O `gpt-oss:120b` apresentou menor latência média e menor consumo médio de tokens totais, mas teve duas reprovações durante a avaliação. O `gemma4:31b-cloud`, modelo atualmente utilizado pelo GurAI, apresentou maior consumo médio de tokens e maior latência, porém concluiu os 39 testes avaliados sem reprovações nesta execução.

Os resultados reforçam que a escolha de um modelo para o GurAI envolve mais do que uma única métrica. Tokens, latência, tamanho das respostas, aderência ao Structured Output e comportamento diante dos guardrails devem ser considerados em conjunto.

Para a Sprint 03, esses dados documentam quantitativamente o comportamento dos dois modelos utilizados no experimento e fornecem a base para justificar a configuração atualmente adotada no projeto.
