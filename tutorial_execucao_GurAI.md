# GurAI — Guia para executar o projeto completo

Este guia descreve como iniciar o GurAI no Windows usando o Git Bash. A arquitetura local possui quatro partes: Ollama local para embeddings, backend Python/FastAPI, frontend Next.js e os serviços Firebase/Firestore utilizados pela aplicação. A geração das respostas conversacionais utiliza o Ollama Cloud.

> **Importante:** execute os comandos a partir das pastas indicadas. Não é necessário abrir o console do Firebase a cada execução, mas o projeto Firebase precisa estar configurado e acessível pelas credenciais da aplicação.

## 1. Requisitos

Instale ou tenha disponível no computador:

- Python compatível com as dependências de `requirements.txt`;
- Node.js e npm;
- Ollama para Windows;
- Git Bash;
- acesso à internet;
- acesso ao projeto Firebase/Firestore e credenciais apropriadas;
- uma chave de API do Ollama Cloud para a geração de respostas.

O repositório deve estar na pasta usada neste exemplo:

```text
C:\Users\gugag\planejamento_chatbot_goodwe
```

Se o projeto estiver em outro caminho, ajuste os comandos `cd` deste guia.

## 2. Configurar as variáveis de ambiente

Existem dois arquivos de ambiente distintos: `.env` na raiz do projeto (Python) e `frontend/.env.local` (Next.js). Não compartilhe esses arquivos nem coloque suas credenciais no Git.

### 2.1 Arquivo `.env` na raiz

Abra ou crie:

```text
C:\Users\gugag\planejamento_chatbot_goodwe\.env
```

Preserve as configurações que já existem e confirme que os parâmetros abaixo estão definidos. Substitua os valores de exemplo pelos valores reais do seu ambiente; nunca use os textos ilustrativos literalmente.

```dotenv
# Protege a API FastAPI. Use uma chave longa e privada.
GURAI_API_KEY=COLOQUE_SUA_CHAVE_PRIVADA_AQUI

# Chave utilizada para o modelo conversacional no Ollama Cloud.
OLLAMA_API_KEY=COLOQUE_SUA_CHAVE_OLLAMA_AQUI

# Embeddings locais com Ollama.
RAG_EMBEDDING_PROVIDER=local
RAG_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_LOCAL_BASE_URL=http://127.0.0.1:11434

# Opcional: seleciona explicitamente o prompt v3.
# Se não definir esta variável, será usado o nome padrão configurado no builder.py.
GURAI_SYSTEM_PROMPT=system_prompt_v3.md
```

Se a variável `GURAI_SYSTEM_PROMPT` não for configurada, confira o valor padrão de `load_system_prompt()` em `src/chain/builder.py` para saber se o projeto selecionará a v2 ou a v3.

A aplicação exige que `GURAI_API_KEY` esteja definida. O frontend deve usar exatamente o mesmo valor em `GURAI_BACKEND_API_KEY`.

### 2.2 Arquivo `frontend/.env.local`

Abra ou crie:

```text
C:\Users\gugag\planejamento_chatbot_goodwe\frontend\.env.local
```

Mantenha suas outras configurações e confirme que existem as seguintes variáveis:

```dotenv
# URL local da API Python. Não acrescente /chat no final.
GURAI_BACKEND_URL=http://127.0.0.1:8000

# Deve ser exatamente igual a GURAI_API_KEY no .env da raiz.
GURAI_BACKEND_API_KEY=COLOQUE_A_MESMA_CHAVE_DA_API_AQUI

# Configuração do projeto Firebase usado pelo frontend.
NEXT_PUBLIC_FIREBASE_API_KEY=VALOR_DO_FIREBASE
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=SEU_PROJETO.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=ID_DO_PROJETO_FIREBASE
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=VALOR_DO_FIREBASE
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=VALOR_DO_FIREBASE
NEXT_PUBLIC_FIREBASE_APP_ID=VALOR_DO_FIREBASE

# Login Google com NextAuth.
GOOGLE_CLIENT_ID=SEU_CLIENT_ID
GOOGLE_CLIENT_SECRET=SEU_CLIENT_SECRET
NEXTAUTH_SECRET=UMA_CHAVE_LONGA_E_PRIVADA
NEXTAUTH_URL=http://localhost:3000

# Necessários para envio de código de acesso por e-mail.
EMAIL_USER=SEU_EMAIL_DE_ENVIO
EMAIL_PASS=SUA_SENHA_DE_APLICATIVO_DO_EMAIL

# Opcional para os tiles do mapa, conforme configuração da aplicação.
NEXT_PUBLIC_CARTO_API_KEY=SUA_CHAVE_CARTO
```

Os valores do Firebase, Google OAuth, serviço de e-mail e Carto devem vir das configurações reais usadas pela equipe. Não invente esses valores.

### 2.3 Credenciais do Firebase Admin / Firestore

O backend do Next.js usa o Firebase Admin com `applicationDefault()`. O computador precisa ter credenciais Google Application Default Credentials autorizadas a acessar o projeto indicado por `NEXT_PUBLIC_FIREBASE_PROJECT_ID`.

Use uma das opções já adotadas pela equipe:

- credenciais padrão do Google Cloud configuradas na máquina; ou
- a variável `GOOGLE_APPLICATION_CREDENTIALS` apontando para o arquivo JSON da conta de serviço autorizado.

Se usar um arquivo de conta de serviço, guarde-o fora do repositório e nunca o envie ao Git ou ao chat. A conta precisa ter as permissões adequadas no Firestore.

O console web do Firebase não precisa ficar aberto enquanto o projeto roda. O Next.js acessa o serviço pela internet usando a configuração e as credenciais disponíveis na máquina.

## 3. Preparação do ambiente Python (somente na primeira configuração)

Abra o Git Bash e vá para a raiz do projeto:

```bash
cd /c/Users/gugag/planejamento_chatbot_goodwe
```

Crie e ative um ambiente virtual, se ainda não existir:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Instale as dependências:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Se o ambiente virtual já existir, ative-o com `source .venv/Scripts/activate`. Caso você tenha configurado o projeto para usar outro ambiente virtual, continue usando o ambiente já utilizado pela equipe.

## 4. Iniciar o Ollama local (embeddings)

O GurAI utiliza `nomic-embed-text` localmente para gerar embeddings e consultar a base documental. Esse serviço precisa estar acessível antes de enviar perguntas ao chat.

1. Abra o aplicativo Ollama no Windows. Se ele não estiver rodando como serviço, abra outro Git Bash e execute:

   ```bash
   ollama serve
   ```

2. Confira se o servidor responde:

   ```bash
   curl http://127.0.0.1:11434/api/tags
   ```

   A resposta deve ser um JSON com os modelos disponíveis.

3. Confira os modelos locais instalados:

   ```bash
   ollama list
   ```

4. Se `nomic-embed-text` não aparecer, faça o download uma única vez:

   ```bash
   ollama pull nomic-embed-text
   ```

Mantenha o Ollama aberto durante o uso do GurAI. Se a API responder que não consegue conectar ao Ollama, verifique se o serviço está executando na porta `11434`.

## 5. Iniciar o backend FastAPI

Abra um terminal Git Bash separado. Inicie o backend **a partir da raiz do projeto** para que o Python encontre `api.py`, os módulos e o `.env` correto:

```bash
cd /c/Users/gugag/planejamento_chatbot_goodwe
source .venv/Scripts/activate
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

Mantenha esse terminal aberto.

Verifique a API abrindo esta URL no navegador:

```text
http://127.0.0.1:8000/health
```

O resultado esperado é:

```json
{"status":"ok"}
```

A documentação interativa do FastAPI também fica disponível em:

```text
http://127.0.0.1:8000/docs
```

O endpoint `/health` confirma que a API está ativa, mas não garante que o Ollama, a autenticação ou a geração de respostas estejam funcionando; esses componentes precisam ser testados separadamente.

## 6. Iniciar o frontend Next.js

Abra um terceiro terminal Git Bash e entre na pasta `frontend`:

```bash
cd /c/Users/gugag/planejamento_chatbot_goodwe/frontend
```

Na primeira instalação, instale as dependências conforme o lockfile:

```bash
npm ci
```

Depois inicie o modo de desenvolvimento:

```bash
npm run dev
```

Mantenha esse terminal aberto. Acesse o site no mesmo computador usando:

```text
http://localhost:3000
```

> Para testar no próprio computador, prefira `localhost` em vez de acessar `http://192.168.x.x:3000`. O acesso por IP via HTTP pode provocar erros de APIs do navegador, como `crypto.randomUUID`, além de problemas de WebSocket/HMR no modo de desenvolvimento.

## 7. Ordem normal de inicialização

Depois que tudo estiver instalado e configurado, cada execução exige manter ativos:

1. **Ollama local** — servidor de embeddings, porta `11434`;
2. **FastAPI** — backend Python, porta `8000`;
3. **Next.js** — frontend e rotas de API, porta `3000`.

O Firebase/Firestore e o Ollama Cloud são serviços remotos; não é necessário iniciar processos locais para eles, mas as credenciais e a conexão com a internet precisam estar funcionando.

## 8. Base documental e ChromaDB

O projeto utiliza uma coleção persistente do ChromaDB em `data/chroma_db/`.

**Não execute a indexação a cada inicialização.** Se a base já estiver indexada e o chat estiver recuperando documentos corretamente, basta iniciar Ollama, FastAPI e frontend.

Execute a indexação somente na primeira configuração do ambiente, se a coleção não existir, ou quando a base documental tiver sido alterada. Para sincronizar o índice, a partir da raiz do projeto e com o Ollama local rodando, execute:

```bash
python indexar_base.py
```

A indexação pode gerar embeddings e alterar os registros persistidos. Não apague `data/chroma_db/` como tentativa genérica de corrigir um problema. Se a indexação falhar, guarde a mensagem de erro e investigue antes de excluir dados.

## 9. Testar o sistema completo

Com os três serviços ativos:

1. Abra `http://localhost:3000`.
2. Entre com um método de autenticação configurado.
3. Envie uma pergunta técnica que possa ser respondida por um dos manuais GoodWe.
4. Confirme que a resposta do GurAI chega ao chat e, quando depender da documentação, contém referência no formato de fonte e página.
5. Teste uma pergunta cuja resposta não esteja na base e verifique se o GurAI reconhece a falta de informação.
6. Se sua conta tiver registros, teste uma pergunta sobre suas sessões pessoais de recarga.

A funcionalidade de login depende do Firebase/Firestore, das credenciais do Firebase Admin, das configurações do Google OAuth e/ou do envio de e-mail. O login por código também exige `EMAIL_USER` e `EMAIL_PASS`, além de um usuário previamente registrado conforme as regras da aplicação.

## 10. Acesso público temporário para demonstração (opcional)

Para disponibilizar o frontend a partir de outra rede, é possível usar um Cloudflare Quick Tunnel, desde que o computador e os serviços continuem ligados. O endereço gerado é temporário.

Para uma demonstração pública, prefira o modo de produção local para evitar os problemas de WebSocket/HMR do Next.js em desenvolvimento. Na pasta `frontend`, execute:

```bash
npm run build
npm run start
```

Em outro terminal, crie o túnel:

```bash
cloudflared tunnel --url http://localhost:3000
```

O Cloudflare exibirá um endereço `https://....trycloudflare.com`. Antes de compartilhar o link, confira as configurações de URL do NextAuth e os endereços autorizados do Google OAuth/Firebase para esse domínio; como o Quick Tunnel muda de endereço, talvez seja necessário atualizar essas configurações e reiniciar o frontend.

Mantenha os terminais necessários abertos durante toda a demonstração. Não exponha endpoints, credenciais ou dados pessoais sem garantir que a autenticação e as verificações de autorização estão funcionando.

## 11. Solução de problemas frequentes

### `npm error ENOENT ... package.json`

Você executou o comando na pasta errada. Entre primeiro na pasta `frontend`:

```bash
cd /c/Users/gugag/planejamento_chatbot_goodwe/frontend
npm run dev
```

### `Failed to connect to Ollama`

O Ollama local não está rodando ou não está acessível. Confira `http://127.0.0.1:11434/api/tags`, execute `ollama serve` se necessário e confirme que `nomic-embed-text` aparece em `ollama list`.

### `POST /chat` retorna `401 Unauthorized`

Compare `GURAI_API_KEY` no `.env` da raiz com `GURAI_BACKEND_API_KEY` em `frontend/.env.local`. Os valores precisam ser exatamente iguais. Não imprima nem compartilhe as chaves para fazer a comparação.

### Frontend retorna `503` ou informa serviço não configurado

Confirme `GURAI_BACKEND_URL` e `GURAI_BACKEND_API_KEY` em `frontend/.env.local`. A URL deve ser `http://127.0.0.1:8000`, sem `/chat` no final. Após alterar arquivos de ambiente, encerre e reinicie `npm run dev`.

### FastAPI retorna `500 Internal Server Error`

Observe o traceback no terminal do FastAPI. O `/health` pode responder `200` mesmo que o RAG falhe ao gerar embeddings, recuperar contexto ou chamar o modelo. Confira primeiro se o Ollama local está ativo e depois verifique a mensagem de erro completa.

### Erros do Firebase Admin ou Firestore

Verifique `NEXT_PUBLIC_FIREBASE_PROJECT_ID`, as credenciais Google Application Default Credentials e as permissões do projeto Firebase. O console web não precisa ficar aberto, mas as credenciais devem funcionar na máquina.

### Erros `crypto.randomUUID` ou WebSocket `/_next/hmr`

Para desenvolvimento local, acesse `http://localhost:3000`. Evite usar o IP da rede local via HTTP quando o navegador exigir um contexto seguro. Para demonstração externa, considere `npm run build` e `npm run start`.

## 12. Segurança

- Nunca compartilhe `.env`, `frontend/.env.local`, tokens, senhas, chaves de API ou arquivos JSON de contas de serviço.
- Não faça commit desses arquivos no Git.
- Mantenha a autenticação ativa antes de expor o site publicamente.
- Use somente credenciais das quais você tenha autorização para dispor.
- Para encerrar, pressione `Ctrl + C` em cada terminal que esteja executando um serviço.
