# planejamento_chatbot_goodwe

# Integrantes

* 569089 - JÚLIA LEMOS SOUZA
* 570021 - VICTOR HENRIQUE NOGUEIRA BEZERRA 
* 573334 -CARLOS HENRIQUE SANTOS DIAS 
* 572131 -ERICK BANHOS DE CASTRO 
* 569305 - ERICK YU XIANG LI 
* 574156 - GUSTAVO ARAUJO RAMOS DA SILVA

# GurAI

Assistente inteligente para gestão operacional de eletropostos.

## Sobre o Projeto

O GurAI é um assistente conversacional especializado em operações de eletropostos e infraestrutura de recarga elétrica, com foco no ecossistema GoodWe.

O projeto busca auxiliar operadores, técnicos de campo e usuários durante atividades relacionadas à recarga, monitoramento de equipamentos, consulta documental, análise de informações operacionais e suporte técnico.

A Sprint 3 evoluiu o núcleo conversacional do projeto com LangChain LCEL, memória por sessão, Structured Output com Pydantic v2, Context Engineering, versionamento do System Prompt e uma camada de guardrails para segurança e controle de escopo.

## Problema

O crescimento da mobilidade elétrica trouxe novos desafios para eletropostos públicos e semi-públicos, principalmente relacionados a:

- Utilização e disponibilidade dos carregadores;
- Monitoramento operacional;
- Gestão energética;
- Autenticação de usuários;
- Tarifação e cobrança;
- Diagnóstico de falhas;
- Consulta de documentação técnica;
- Suporte operacional.

Além disso, informações de carregadores podem estar distribuídas em manuais, datasheets, mapas MODBUS e dados operacionais, tornando a consulta manual mais lenta e sujeita a erros.

O GurAI busca reduzir esse tempo por meio de uma interface conversacional capaz de consultar dados operacionais e documentação técnica, mantendo regras de escopo e prevenção de alucinação.

### Principais desafios identificados

- Sobrecarga energética;
- Dificuldades de autenticação;
- Suporte operacional insuficiente;
- Gestão manual dos carregadores;
- Consulta manual de documentação técnica;
- Interpretação de códigos de erro e registradores MODBUS;
- Necessidade de respostas rápidas e contextualizadas.

---

# Persona Utilizada

## Técnico de Campo

A persona principal do GurAI é o Técnico de Campo, profissional que necessita consultar rapidamente informações operacionais e técnicas dos carregadores.

### Principais responsabilidades

- Verificar disponibilidade dos carregadores;
- Consultar status de equipamentos;
- Diagnosticar falhas operacionais;
- Consultar códigos de erro;
- Consultar manuais e datasheets;
- Interpretar informações MODBUS;
- Monitorar consumo energético da planta;
- Encaminhar situações que exigem intervenção humana especializada.

### Principais dores identificadas

- Dificuldade em localizar rapidamente a causa de falhas;
- Consulta manual de datasheets e manuais técnicos;
- Necessidade de acessar múltiplas fontes para diagnóstico;
- Tempo elevado de resposta para problemas operacionais;
- Interpretação de códigos de erro e registradores MODBUS.

### Perguntas típicas da persona

- O que significa o erro 0x0001?
- Qual a potência nominal do GW22K-HCA-20?
- Quais carregadores estão disponíveis?
- Como está o charger_01?
- Qual a energia total utilizada?

### Personas secundárias

Embora o foco principal seja o Técnico de Campo, o sistema também pode auxiliar:

- Operadores do eletroposto;
- Estabelecimentos comerciais;
- Usuários finais dos carregadores.

Esses perfis são secundários em relação ao suporte técnico e operacional especializado.

---

# Contexto Escolhido

## Contexto A — Operação Comercial de Eletropostos

O GurAI foi desenvolvido considerando o contexto de eletropostos comerciais e semi-públicos.

### Justificativas da escolha

1. **Grande volume de usuários**

Eletropostos comerciais podem atender múltiplos usuários diariamente, aumentando a necessidade de suporte automatizado.

2. **Complexidade operacional**

A operação envolve disponibilidade dos carregadores, monitoramento energético, autenticação, consulta técnica e resolução de falhas.

3. **Necessidade de suporte rápido**

Falhas em carregadores podem impactar a operação do estabelecimento e a experiência do usuário.

4. **Integração com protocolos industriais**

O ambiente utiliza tecnologias e protocolos voltados ao monitoramento e controle de equipamentos, como MODBUS e OCPP.

5. **Escalabilidade**

A solução pode futuramente ser aplicada a redes com dezenas ou centenas de carregadores.

---

# Problema Central

Os carregadores GoodWe disponibilizam diversas informações operacionais e técnicas. Entretanto, a interpretação dessas informações pode exigir consulta manual a diferentes documentos e sistemas.

O GurAI busca reduzir esse tempo através de uma interface conversacional capaz de:

- Consultar dados operacionais;
- Consultar manuais e datasheets;
- Interpretar informações MODBUS;
- Recuperar informações de contexto conversacional;
- Responder de forma estruturada quando necessário;
- Evitar a invenção de especificações ausentes na documentação.

---

# Contexto utilizado pelo modelo

O GurAI trabalha com contexto operacional, documental e conversacional.

Atualmente, o sistema utiliza dados operacionais simulados e documentação técnica GoodWe. Integrações reais com infraestrutura de carregadores permanecem como evolução futura.

## Dados utilizados

- Status do carregador;
- Potência e variáveis elétricas;
- Sessões de recarga;
- Energia consumida;
- Disponibilidade dos carregadores;
- Informações técnicas dos modelos GoodWe;
- Códigos e informações MODBUS;
- Histórico conversacional;
- Regras de escopo e segurança.

A arquitetura foi preparada para futuras integrações com fontes operacionais reais.

---

# Tecnologias

## Backend

### Python

Python é utilizado como linguagem principal do backend devido à integração com bibliotecas de IA, facilidade de desenvolvimento e capacidade de prototipação.

### LangChain

O núcleo conversacional foi refatorado utilizando LangChain LCEL.

A cadeia principal segue o conceito:

```text
ChatPromptTemplate → ChatOllama → Output Parser
```

A Sprint 3 utiliza também:

- `RunnableWithMessageHistory`;
- Structured Output;
- Pydantic v2;
- Context Engineering.

## IA

### Ollama Cloud

O projeto utiliza `ChatOllama` com acesso ao Ollama Cloud.

Modelo atualmente utilizado pelo GurAI:

```text
gemma4:31b-cloud
```

Durante a Sprint 3, também foi realizado comparativo com:

```text
gpt-oss:120b
```

### Parâmetros atuais

```text
temperature = 0.3
top_p = 0.9
num_predict = 1200
```

O valor baixo de `temperature` favorece respostas mais consistentes, enquanto `top_p` controla o conjunto de tokens mais prováveis considerados durante a geração.

## Memória Conversacional

A Sprint 3 utiliza memória por sessão com:

* python
ConversationTokenBufferMemory(
    llm=llm,
    max_token_limit=1000,
    return_messages=True
)


A memória é associada a um `session_id` por meio de `RunnableWithMessageHistory`.

O limite de `1000` tokens controla a quantidade de histórico mantida no contexto da memória.

## Structured Output

O sistema utiliza schemas Pydantic v2 para estruturar informações do domínio de recarga.

Principais schemas:

- `ConsultaRecarga`;
- `ConsultaPotenciaTotal`;
- `ConsultaCarregadoresDisponiveis`;
- `ConsultaCarregadoresAtivos`;
- `ConsultaEnergiaTotal`.

Foram utilizados `field_validator` para validar identificadores, valores numéricos e estruturas específicas.

## Context Engineering

O System Prompt foi versionado durante a Sprint 3:

```text
prompts/system_prompt_v1.md
prompts/system_prompt_v2.md
```

A versão 2 utiliza organização estruturada com XML tags e regras explícitas de:

- Escopo;
- Segurança;
- Prevenção de alucinação;
- Uso da documentação;
- Controle do contexto.

Medição atual:

```text
System Prompt v1: 1724 tokens
System Prompt v2: 2715 tokens
Diferença: +991 tokens
```

## RAG e documentação

O GurAI utiliza documentação GoodWe para consultas técnicas.

Documentos principais:

- `GW_HCA-G2_Datasheet-PT.pdf`;
- `Mapa-MODBUS_HCA-G2.pdf`;
- `GW_HCA-G2_User-Manual-PT.pdf`.

A recuperação documental é utilizada para evitar a geração de especificações que não estejam presentes na documentação disponível.

## Guardrails e segurança

A Sprint 3 introduziu uma camada dedicada de controle de segurança:

```text
src/guardrails/
├── scope_validator.py
└── moderation.py
```

Os guardrails incluem:

- Controle de escopo;
- Detecção de jailbreak;
- Proteção contra prompt injection;
- Bloqueio de instruções de instalação ou intervenção elétrica;
- Prevenção de associações não documentadas entre `charger_XX` e modelos;
- Recusa de informações fora do domínio operacional.

Detecções como jailbreak e determinadas intervenções elétricas podem ser realizadas de forma determinística antes da chamada ao modelo, reduzindo consumo de tokens e latência.

---

# Avaliação da Sprint 3

A Sprint 3 foi avaliada utilizando um conjunto de **39 testes** envolvendo:

- Operação;
- Consulta documental;
- Conversação;
- Memória;
- Structured Output;
- Jailbreak;
- Prompt injection;
- Segurança elétrica;
- Escopo;
- Jurídico;
- Financeiro;
- Suporte;
- Prevenção de alucinação.

Na execução final do modelo atualmente utilizado:

```text
gemma4:31b-cloud
39 testes avaliados
39 aprovados
0 reprovados
```

Também foi realizado um comparativo com `gpt-oss:120b` utilizando o mesmo conjunto de testes e os mesmos parâmetros de geração.

No comparativo:

```text
GPT-OSS 120B
37 aprovados
2 reprovados

Gemma 4 31B
39 aprovados
0 reprovados
```

Os dois modelos foram avaliados sob:

```text
temperature = 0.3
top_p = 0.9
num_predict = 1200
```

---

# Versões do Projeto

## 0.01

- Alucinações frequentes;
- Dependência de dados simulados;
- Sem consulta aos manuais;
- Funcionalidade conversacional básica.

Porém:

- Respondia às perguntas;
- Funcionava como protótipo;
- Apresentava arquitetura inicial funcional.

---

## 0.02

- Algumas respostas sem sentido;
- Limitações na camada de dados;
- Necessidade de normalização textual;
- Alucinações ainda presentes.

Porém:

- Melhor atendimento aos prompts;
- Interpretação dos dados simulados;
- Memória de contexto funcionando.

---

## 0.1

- Versão funcional do sistema;
- Lógica para leitura de dados simulados;
- Streamlit implementado;
- Regras de segurança;
- Código desacoplado da interface.

Próximos objetivos:

- Leitura real dos dados;
- Consulta aos manuais;
- Intents;
- Melhoria da interface.

---

## 0.2

Implementações:

- Painéis na sidebar;
- Detalhes dos carregadores;
- Informações operacionais na interface.

Próximas atualizações:

- Consulta de PDFs;
- Intents.

---

## 0.3 (beta — MVP)

Implementações:

- Sidebar operacional;
- Painel de monitoramento;
- Consulta detalhada de carregadores;
- RAG básico utilizando PDFs;
- Intents;
- Normalização de texto;
- Redução de alucinações;
- Sistema de nova conversa;
- Consulta documental GoodWe.

Limitações:

- Dados ainda simulados;
- Sem integração real com OCPP;
- Sem integração real com MODBUS;
- Sem persistência em banco de dados;
- Sem histórico persistente de conversas.

---

# Sprint 3

A Sprint 3 teve como objetivo reconstruir o núcleo conversacional utilizando recursos referente ao Módulo 1.

### Implementações

- Refatoração do núcleo para LangChain LCEL;
- `ChatPromptTemplate`;
- `ChatOllama`;
- Output Parser;
- Memória por sessão;
- `RunnableWithMessageHistory`;
- `ConversationTokenBufferMemory`;
- Structured Output;
- Pydantic v2;
- `field_validator`;
- Context Engineering;
- System Prompt versionado;
- XML tagging;
- Medição de tokens com `tiktoken`;
- Guardrails de escopo;
- Proteção contra jailbreak;
- Proteção contra prompt injection;
- Segurança para intervenções elétricas;
- Prevenção de alucinações;
- Avaliação quantitativa da solução.

### Resultado

A versão da Sprint 3 possui um núcleo conversacional mais estruturado, com validação de dados, memória por sessão, regras explícitas de contexto e mecanismos de segurança antes e durante a geração.

---

# Próximos Passos

- Integração real com carregadores GoodWe;
- Integração com OCPP;
- Integração com MODBUS;
- Persistência de dados;
- Sistema de múltiplas conversas;
- Dashboard avançado;
- Estatísticas históricas;
- Controle de permissões;
- Sistema de login;
- Evolução da integração com fontes operacionais reais.

---

# Funcionalidades Atuais

Atualmente o GurAI é capaz de:

- Consultar status dos carregadores;
- Exibir potência total da planta;
- Exibir energia total consumida;
- Exibir carregadores disponíveis;
- Exibir carregadores em uso;
- Consultar informações técnicas dos manuais GoodWe;
- Consultar informações MODBUS;
- Utilizar memória conversacional por sessão;
- Utilizar RAG para consulta documental;
- Utilizar intents para interpretar diferentes formas de perguntas;
- Produzir Structured Output com Pydantic;
- Operar através do Streamlit;
- Aplicar guardrails de escopo e segurança;
- Reduzir alucinações por meio de validação documental.

---

# Link do vídeo de demonstração do GurAI

YouTube:

https://youtu.be/IAOqCMTZQ4c

---

# Instalação

## 1. Clonar o projeto

```bash
git clone https://github.com/Hiero-o/planejamento_chatbot_goodwe.git
cd planejamento_chatbot_goodwe
```

## 2. Criar ambiente virtual

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

## 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

# Configuração do Ollama Cloud

O GurAI utiliza modelos disponibilizados pelo Ollama Cloud.

1. Acesse:

https://ollama.com/

2. Crie ou acesse sua conta.

3. Acesse **Settings → Keys**.

4. Crie uma API Key.

5. Crie um arquivo `.env` na raiz do projeto.

6. entre em .env.example, mude o nome do arquivo para apenas .env e:

```env
OLLAMA_API_KEY=sua_api_key_aqui
```

**Nunca publique a API key no repositório.**

---

# Como Executar

Com o ambiente virtual ativo:

```bash
streamlit run streamlit_app.py
```

---

# Exemplos de Perguntas

```text
Qual a potência total da planta?

Quais carregadores estão disponíveis?

Quais carregadores estão em uso?

Como está o charger_01?

Qual a energia total utilizada?

O que significa o erro 0x0001?

Qual a potência nominal do carregador HCA G2?

Qual a corrente nominal do modelo GW22K-HCA-20?
```

---


# Objetivo Final

O GurAI busca melhorar a experiência de operação de eletropostos, reduzir o tempo de consulta técnica e apoiar o gerenciamento de informações operacionais por meio de IA.

A evolução planejada inclui integração com infraestrutura real de recarga, protocolos de comunicação, persistência de dados e ferramentas avançadas de monitoramento, mantendo como princípios a segurança, o controle de escopo e a utilização de informações documentadas.
