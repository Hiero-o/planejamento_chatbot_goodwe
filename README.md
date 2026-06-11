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

### Principais desadios identificados:

- Sobrecarga Energética;
- Dificuldades de autenticação de usuários;
- Suporte insuficiente;
- Gestão manual dos carregadores;
- Cobranças complexas;
- Horários de pico energético.

---

# Persona Utilizada

## Técnico de campo.

O técnico de campo, especializado em operações de eletropostos.

A escolha dessa persona se deu pela necessidade de oferecer respostas rápidas, técnicas e objetivas para usuários de sessão de recarga, além de auxiliar operadores técnicos e estabelecimento em situações operacionais e comerciais.

O chatbot atua como intermediador entre usuário, sistema e suporte técnico, reduzindo falhas operacionais e melhorando a experiência de utilização dos carregadores.

----

# Contexto utilizado pelo modelo.

O chatbot utilizará contexto operacional, energético e comercial obtido através de integração com banco de dados, APIs, protolo MODBUS e OCPP.

O objetico da utilização desses dados é permitir respostas contextualizadas, maior precisão operacional e suporte inteligente durante as sessões de recarga.

## Dados utilizados pelo modelo
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

### Firebase
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

### OCPP
O OCPP (Open Charge Point Protocol) será utilizado como principal protocolo de comunicação entre o sistema e os carregadores.

#### Vantagens
- Padrão mundial para eletropostos;
- Monitoramento remoto;
- interoperabilidade entre fabricantes;
- controle operacional avançado.

#### Desvantagens
- Implementação mais complexa;
- Maior necessidade de gerenciamento de comunicação.

### MODBUS

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
- bem limitadinho coitado

## 0.02
- Algumas respostas sem sentido
- Limitação de banco de dados ainda presente, provavelmente até o final do projeto
- Normalizar o texto para remoção de acentos e formatações diferentes deverá ser uma prioridade nas próximas versões, deixando o prompt sem acentos, letras maiusculas etc..

Porém:

- A ia está atendendo melhor aos prompts, mas ainda inventa informações quando não sabe.
- A ia está consehuindo acessar os dados simulados e interpretá-los.
- A memória de contexto está funcionando bem!

---

# Implementações futuras?

- Múltiplas conversas
- Histórico lateral
- Seleção de conversa
- Persistência em Firebase

---

# Objetivo Final

O projeto busca melhorar a experiência de usuários de veículos elétricos, otimizar o consumo energético dos eletropostos e automatizar processos operacionais através de um chatbot integrado ao ecossistema de recarga elétrica da GoodWe.
Além disso, a solução planeja reduzir falhas operacionais, melhorar o suporte técnico aos usuários e contribuir para gestão energética mais eficiente e sustentável.
