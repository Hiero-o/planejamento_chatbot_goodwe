# planejamento_chatbot_goodwe

# GurAI
GurAI
Assistente inteligente para gestão operacional de eletropostos.

# Sobre o Projeto

O crescimento da mobilidade elétrica troiuxe novos desafios para eletropostos públicos e semi-públicos, principalmente relacionados ao controle energético, autenticação de usuários, tarifação dinâmica e suporte operacional.
O projeto consiste na elaboração de um Chatbot voltado para auxiliar usuários, estabelecimentos comerciais e operadores técnicos durante o processo de recarga, oferecendo suporte aos usários finais, ao suporte operacional, análise de consumo energético e recomendações inteligentes de uso.

# Integrantes

569089 - JÚLIA LEMOS SOUZA
570021 - VICTOR HENRIQUE NOGUEIRA BEZERRA
573334 - CARLOS HENRIQUE SANTOS DIAS
572131 - ERICK BANHOS DE CASTRO
569305 - ERICK YU XIANG LI
574156 - GUSTAVO ARAUJO RAMOS DA SILVA


## Problema:

Durante as últimas décadas, carros elétricos ganharam espaço no setor automobilístico mundial. Entre 2020 e os dias atuais, a busca pela redução do uso de fontes não renováveis de energia ganhou grande destaque.

O crescimento de veículos elétricos, trouxe desafios relacionados à infraestrutura energética no Brasil, já que muitos estabelecimentos ainda não estão preparados para suportar a alta demana elétrica necessária para operações de recarga.

Além disso, existem problemas relacionados à:

- Autenticação de usuários;
- Utilização dos carregadores;
- Tarifação aplicada;
- Suporte operacional;
- Gestão energética;
- cobrança automatizada.

Outro problrma importante é a ausência de sistemas inteligentes capazes de auxiliar usuários, operadores técnicos e estabelecimentos durante sessões de recarga.

### Principais desafios identificados:

- Sobrecarga Energética;
- Dificuldades de autenticação de usuários;
- Suporte insuficiente;
- Gestão manual dos carregadores;
- Cobranças complexas;
- Horários de pico energético.

---

# Persona Utilizada

## Técnico de campo.

A escolha dessa persona se deu pela necessidade de oferecer respostas rápidas, técnicas e objetivas para usuários de sessão de recarga, além de auxiliar operadores técnicos e estabelecimento em situações operacionais e comerciais.

O chatbot atua como intermediador entre usuário, sistema e suporte técnico, reduzindo falhas operacionais e melhorando a experiência de utilização dos carregadores.

---

## Persona Principal: Técnico de Campo

O Técnico de Campo é o profissional responsável pela instalação, monitoramento, diagnóstico e manutenção dos carregadores veiculares presentes nos eletropostos.

### Principais responsabilidades

* Verificar disponibilidade dos carregadores;
* Diagnosticar falhas operacionais;
* Consultar códigos de erro;
* Realizar testes de comunicação MODBUS e OCPP;
* Auxiliar usuários em problemas de autenticação;
* Monitorar consumo energético da planta.

### Principais dores identificadas

* Dificuldade em localizar rapidamente a causa de falhas;
* Consulta manual de datasheets e manuais técnicos;
* Necessidade de acessar múltiplos sistemas para diagnóstico;
* Alto tempo de resposta para atendimento operacional;
* Interpretação de códigos de erro e registradores MODBUS.

### Perguntas típicas da persona

* O que significa o erro 0x0001?
* Qual a potência nominal do GW22K-HCA-20?
* Quais carregadores estão disponíveis?
* Qual carregador está apresentando falha?
* Qual a energia total consumida hoje?

### Personas secundárias

Embora o foco principal seja o Técnico de Campo, o sistema também pode auxiliar:

* Operadores do eletroposto;
* Estabelecimentos comerciais;
* Usuários finais dos carregadores.

Esses perfis são considerados secundários e recebem suporte limitado quando comparados ao suporte técnico especializado.


---


# Contexto Escolhido

## Contexto A — Operação Comercial de Eletropostos

O GurAI foi desenvolvido considerando o Contexto A, voltado para eletropostos comerciais e semi-públicos.

### Justificativas da escolha

1. Grande volume de usuários

Diferentemente de ambientes residenciais ou condominiais, eletropostos comerciais atendem múltiplos usuários diariamente, aumentando a necessidade de suporte automatizado.

2. Complexidade operacional

A operação envolve autenticação, tarifação, monitoramento energético, disponibilidade dos carregadores e resolução de falhas técnicas.

3. Necessidade de suporte técnico rápido

Falhas em carregadores podem impactar diretamente a receita do estabelecimento e a experiência do usuário.

4. Integração com protocolos industriais

O ambiente comercial exige monitoramento utilizando protocolos como MODBUS e OCPP, aumentando a necessidade de ferramentas inteligentes de suporte.

5. Escalabilidade

A solução poderá ser aplicada em redes de eletropostos com dezenas ou centenas de carregadores.

---

## Expansão para Contexto Condominial

Embora o foco principal do GurAI esteja na operação comercial de eletropostos, a arquitetura foi projetada para permitir futura aplicação em ambientes condominiais.

Nesse cenário, moradores poderiam utilizar cartões de autenticação individuais ou coletivos com sistema de login, para identificação durante as sessões de recarga.

A solução permitiria:

- Controle de consumo por morador;
- Rateio energético atrelado ao apartamento;
- Histórico individual de utilização;
- Controle de acesso aos carregadores;
- Consulta de informações operacionais através do chatbot.

---

## Problema Central

Além das falhas operacionais tradicionais, o ambiente de recarga elétrica apresenta desafios relacionados ao gerenciamento de sessões de recarga, tarifação, autenticação de usuários e monitoramento energético.

Os carregadores GoodWe disponibilizam uma grande quantidade de informações operacionais através de protocolos como MODBUS e OCPP. Entretanto, a interpretação desses dados normalmente exige consulta manual a documentações técnicas, aumentando o tempo necessário para diagnóstico e resolução de problemas.

O GurAI busca reduzir esse tempo através da utilização de Inteligência Artificial, permitindo acesso rápido às informações operacionais e documentais do ecossistema GoodWe.


---

# Contexto utilizado pelo modelo.

O chatbot utilizará contexto operacional, energético e comercial obtido através de integração com banco de dados, APIs, protolo MODBUS e OCPP.

O objetico da utilização desses dados é permitir respostas contextualizadas, maior precisão operacional e suporte inteligente durante as sessões de recarga.

## Dados que serão utilizados pelo modelo
- Status do carregador (Disponibilidade e funcionamento);
- Potência energética disponível;
- Sessões de recarga ativas;
- Demanda energética do estabelecimento;
- Horários de pico de consumo;
- Tarifação dinâmica;
- Logs operacionais e falhas operacionais;
- Autenticação de usuários;
- Validação de recargas;
- Histórico de sessão e consumo energético.

A utilização dessas informações permitirá que o chatbot realize recomendações inteligentes de horários de recarga, reduza riscos de sobrecarga energética e ofereça suporte operacional mais eficiente aos usuários e operadores técnicos.

---

# Tecnologias escolhidas

## backend:

### Python

O Python foi escolhido como linguagem principal do backend devido à sua excelente integração com ferramentas de Inteligência Artificial, ampla quantidade de bibliotecas robustas e facilidade de prototipação.

#### Vantagens
- Ótima integração com IA;
- Desenvolvimento rápido;
- grande comunidade;
- Facilidade de manutenção.

#### Desvantagens
- Menor desempenho bruto quando comparado a linguagens como Rust ou GO
- Maior consumo de recursos em aplicações altamente escaláveis.

---

## IA:

### Ollama

O Ollama foi escolhido por permitir execução local de modelos de linguagem, oferecendo maior flexibilidade, personalização e redução de custos operacionais relacionados ao uso de APIs externas.

#### Vantagens
- Execução local;
- Menor dependência de serviços externos;
- Boa personalização de modelos;
- Redução de custos.

#### Desvantagens
- Necessidade de hardware mais robusto;
- Modelos locais podem possuir desempenho inferior quando comparados a modelos proprietários maiores.

---

## Banco de Dados:

### Firebase (Implementação futura)
O Firebase foi escolhido devido ao seu suporte a comunicação em tempo real, escalabilidade automática e integração simplificada com aplicações web e mobile, fatores importantes para o monitoramento de sessões de recarga e controle operacional.

#### Vantagens
- Comunicação em tempo real nativa;
- Fácil integração com aplicações web e mobile;
- Escalabilidade automática;
- Alta disponibilidade e confiabilidade;
- Autenticação e serviços integrados;
- Agilidade no desenvolvimento do sistema.
#### Desvantagens
- Menor suporte a relacionamentos complexos;
- Consultas avançadas mais limitadas em comparação a bancos SQL;
- Dependência do ecossistema da Google;
- Custos podem aumentar conforme o volume de acessos e operações.

---

## Comunicação dos carregadores

### OCPP (Integração futura)
O OCPP (Open Charge Point Protocol) será utilizado como principal protocolo de comunicação entre o sistema e os carregadores.

#### Vantagens
- Padrão mundial para eletropostos;
- Monitoramento remoto;
- interoperabilidade entre fabricantes;
- controle operacional avançado.

#### Desvantagens
- Implementação mais complexa;
- Maior necessidade de gerenciamento de comunicação.

### MODBUS (Integração futura) - (Atualmente = dados simulados)

O protocolo MODBUS será utilizado para comunicação direta com hardware e leitura de sensores elétricos.

#### Vantagens
- Simples implementação;
- Amplamente utilizado na indústria;
- Eficiência na leitura de sensores e variáveis elétricas.

#### Desvantagens
- Menos adequado para gerenciamento completo de sessões de recarga;
- Menor flexibilidade para aplicações modernas na rede.

---

# Versões

## 0.01
- Alucina MUITO;
- depende de dados simulados;
- não acessa manuais;

Porém:

- Responde as perguntas
- Funciona!
- bem limitado

---

## 0.02
- Algumas respostas sem sentido
- Limitação de banco de dados ainda presente, provavelmente até o final do projeto
- Normalizar o texto para remoção de acentos e formatações diferentes deverá ser uma prioridade nas próximas versões, deixando o prompt sem acentos, letras maiusculas etc..

Porém:

- A IA está atendendo melhor aos prompts, mas ainda inventa informações quando não sabe.
- A IA está conseguindo acessar os dados simulados e interpretá-los.
- A memória de contexto está funcionando bem!

---

## 0.1
- Versão versão funcional do sistema
- Aplicação de lógica para leitura de dados simulados
- Respostas corretas, sem quebras ou alucinações, quando, dentro do prompt esperado
- Streamlit implementado e funcionando
- Regras de segurança testadas e aplicadas
- Códigos funcionam independete do streamlit, se quisermos trocar e usar REACT ou similar para usar o modelo, será mais fácil.

Porém:

- Implementar leitura real de dados seria um diferencial
- Implementar leitura de manuais para o modelo
- Implementar intent nas perguntas para melhorar o GurAI
- Melhorar interface gráfica do streamlit (muito básico)

---

## 0.2

Todas da 0.1, com implementações:
- Adição de painéis na sidebar
- Mostrando detalhes dos chargers na sidebar

Próximas atualizações:

- Consulta PDFs
- Intent nas perguntas.


---

## 0.3 (beta - MVP)

Implementações:

- Sidebar operacional
- Painel de monitoramento
- Consulta detalhada de carregadores
- RAG básico utilizando PDFs
- Intents para interpretação de perguntas
- Normalização de texto
- Redução de alucinações
- Sistema de nova conversa (Limpa chat)
- Consulta documental GoodWe

Limitações atuais:

- Dados ainda simulados
- Sem integração real com OCPP
- Sem integração real com MODBUS
- Sem persistência em banco de dados
- Sem historico real de conversas

# Próximos Passos

- Integração real com carregadores GoodWe;
- Integração com protocolo OCPP;
- Integração com protocolo MODBUS;
- Persistência de dados em Firebase;
- Sistema de múltiplas conversas;
- Dashboard avançado;
- Estatísticas históricas;
- Controle de permissões por usuário;
- Sistema de Login integrado


---

# Funcionalidades Atuais

Atualmente o GurAI é capaz de:

- Consultar status dos carregadores;
- Exibir potência total da planta;
- Exibir energia total consumida;
- Exibir carregadores disponíveis;
- Exibir carregadores em uso;
- Interpretar informações técnicas dos manuais GoodWe;
- Consultar informações do protocolo MODBUS;
- Utilizar memória de conversa;
- Utilizar RAG (Retrieval-Augmented Generation) para consulta documental;
- Utilizar intents para compreender diferentes formas de perguntas;
- Operar através de interface gráfica desenvolvida em Streamlit;
- Reduzir alucinações através de validação documental.


# Link do vídeo de demonstração do GurAI

YouTube: https://youtu.be/IAOqCMTZQ4c

---

# Instalação

## 1. Clonar o projeto

git clone https://github.com/Hiero-o/planejamento_chatbot_goodwe.git

cd planejamento_chatbot_goodwe

## 2. Criar ambiente virtual

TERMINAL
CMD, POWERSHELL, GIT BASH...

Windows:

python -m venv venv

venv\Scripts\activate

## 3. Instalar dependências

terminal

pip install -r requirements.txt

# Instalação do Ollama

O GurAI utiliza modelos em nuvem do ollama.

Vá até o site do Ollama:

https://ollama.com/

Crie sua conta

ícone do canto superior direito > Settings > Keys > Add API key > nome de sua escolha > Generate API Key > copiar

Próximo passo:

Terminal

cd diretório de instalação do projeto

cd planejamento_chatbot_goodwe

touch .env

code .

abrir o arquivo .env > digitar OLLAMA_API_KEY=sua_api_key_aqui

salvar

# Como Executar

Com o ambiente virtual ativo:

terminal

streamlit run streamlit_app.py

# Exemplos de Perguntas

Qual a potência total da planta?

Quais carregadores estão disponíveis?

Quais carregadores estão em uso?

Como está o charger_01?

Qual a energia total utilizada?

O que significa o erro 0x0001?

Qual a potência nominal do carregador HCA G2?

Qual a corrente nominal do modelo GW22K-HCA-20?


# Objetivo Final

O projeto busca melhorar a experiência de usuários de veículos elétricos, otimizar o consumo energético dos eletropostos e automatizar processos operacionais através de um chatbot integrado ao ecossistema de recarga elétrica da GoodWe.
Além disso, a solução planeja reduzir falhas operacionais, melhorar o suporte técnico aos usuários e contribuir para gestão energética mais eficiente e sustentável.
