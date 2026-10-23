# GurAI — guia e inicializador local (Windows)

Esta pasta é um **kit auxiliar** para ser copiado para a raiz do repositório GurAI. Ela não substitui nem reorganiza o projeto. O inicializador usa arquivos existentes na raiz: `requirements.txt`, `indexar_base.py`, `.env` e `frontend/`.

## O que esta pasta contém

- `gerenciar_gurai.py`: menu interativo para preparar dependências, conferir configuração, indexar a base sob confirmação e abrir os três serviços locais.
- `PREPARAR_AMBIENTE.bat`: abre o gerenciador.
- `INICIAR_GURAI.bat`: abre o gerenciador; escolha a opção 4 para iniciar os serviços.
- `INDEXAR_BASE.bat`: abre o gerenciador; escolha a opção 3 para indexar com confirmação.
- `modelos/env.raiz.example`: modelo de variáveis para `.env` na raiz do projeto.
- `modelos/env.frontend.example`: modelo para `frontend/.env.local`.

## Requisitos

1. Windows 10/11.
2. Python instalado e disponível no terminal como `python`.
3. Node.js/npm instalado.
4. Ollama instalado para Windows.
5. Acesso à internet para instalar dependências e chamar o Ollama Cloud.
6. Credenciais próprias para Ollama Cloud, Firebase/Firestore, Google OAuth e e-mail conforme os métodos de autenticação habilitados no projeto.

Use a versão de Python com a qual o repositório funciona no computador da equipe. O gerenciador cria `.venv` local ao preparar o ambiente e instala o `requirements.txt` fornecido pelo próprio projeto.

## Instalação limpa — primeira execução

1. Extraia/copie a pasta `COMO EXECUTAR O GURAI` diretamente na raiz do projeto, ao lado de `api.py`, `indexar_base.py`, `requirements.txt` e da pasta `frontend/`.
2. Abra a pasta do projeto no Windows.
3. Execute `COMO EXECUTAR O GURAI/PREPARAR_AMBIENTE.bat` ou, no terminal da raiz:

   ```powershell
   python "COMO EXECUTAR O GURAI/gerenciar_gurai.py"
   ```

4. Escolha **1 — Preparar ambiente**. O script cria `.venv` se necessário, instala `requirements.txt`, executa `npm ci` na pasta `frontend/` e cria os arquivos `.env`/`.env.local` a partir dos modelos apenas se eles ainda não existirem. **Arquivos de ambiente existentes nunca são sobrescritos.**
5. Edite os arquivos `.env` (raiz) e `frontend/.env.local` conforme a seção seguinte. Os modelos só contêm valores ilustrativos.
6. Volte ao menu e escolha **2 — Verificar ambiente e variáveis**. Corrija os itens em falta.
7. Escolha **4 — Iniciar todos os serviços**.

## Configurar variáveis de ambiente

### `.env` na raiz

O modelo fica em `COMO EXECUTAR O GURAI/modelos/env.raiz.example`. O gerenciador o copia para a raiz como `.env` se esse arquivo não existir. Defina pelo menos:

```dotenv
GURAI_API_KEY=CHAVE_PRIVADA_LONGA
OLLAMA_API_KEY=CHAVE_DO_OLLAMA_CLOUD
RAG_EMBEDDING_PROVIDER=local
RAG_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_LOCAL_BASE_URL=http://127.0.0.1:11434
```

`GURAI_API_KEY` é uma chave privada criada pela equipe para proteger a API. `OLLAMA_API_KEY` é a chave real do Ollama Cloud usada na geração das respostas. Não use os valores ilustrativos dos modelos.

`GURAI_SYSTEM_PROMPT` é opcional. Configure `GURAI_SYSTEM_PROMPT=system_prompt_v3.md` apenas se esse arquivo existir e a equipe tiver decidido usar v3. Sem essa variável, vale o padrão definido em `src/chain/builder.py`.

### `frontend/.env.local`

O modelo fica em `COMO EXECUTAR O GURAI/modelos/env.frontend.example`. Ele cobre as variáveis usadas pelo frontend:

- `GURAI_BACKEND_URL=http://127.0.0.1:8000`
- `GURAI_BACKEND_API_KEY` — deve ser **idêntica** à `GURAI_API_KEY` da raiz.
- Variáveis `NEXT_PUBLIC_FIREBASE_*` do projeto Firebase real.
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `NEXTAUTH_SECRET` e `NEXTAUTH_URL=http://localhost:3000` para NextAuth.
- `EMAIL_USER` e `EMAIL_PASS` se usar login por código de e-mail.
- `NEXT_PUBLIC_CARTO_API_KEY` se a configuração do mapa usar essa chave.

Preencha esses valores com as configurações reais autorizadas pelo grupo. Não há credenciais de exemplo válidas neste pacote.

### Firebase Admin / Firestore

O código do frontend usa `applicationDefault()` do Firebase Admin. Configure Application Default Credentials na máquina ou defina `GOOGLE_APPLICATION_CREDENTIALS` para apontar para um JSON autorizado de conta de serviço. Guarde esse JSON fora do repositório, não o envie a ninguém e não o versione. O Console do Firebase não precisa ficar aberto, mas a conta precisa ter permissões no projeto correto.

## Uso diário — iniciar tudo

Depois da configuração inicial, no terminal da raiz execute:

```powershell
python "COMO EXECUTAR O GURAI/gerenciar_gurai.py"
```

Escolha **4 — Iniciar Ollama + FastAPI + frontend**. O script:

1. Valida arquivos e variáveis necessárias sem imprimir credenciais.
2. Verifica se o Ollama responde em `http://127.0.0.1:11434`; se não, tenta abrir `ollama serve` em outra janela.
3. Confirma a instalação de `nomic-embed-text` e pergunta antes de baixá-lo se faltar.
4. Abre janelas separadas para o FastAPI e o Next.js.

Acesse:

- Frontend: <http://localhost:3000>
- FastAPI health: <http://127.0.0.1:8000/health>
- Documentação interativa do FastAPI: <http://127.0.0.1:8000/docs>
- Ollama local: <http://127.0.0.1:11434/api/tags>

Deixe as janelas abertas durante o uso. Para encerrar cada serviço, use `Ctrl+C` na janela correspondente.

## Indexar ou atualizar documentos no ChromaDB

**Não indexe em cada inicialização.** A indexação modifica/sincroniza a coleção persistente. Faça isso somente na primeira configuração, quando documentos forem adicionados/alterados ou quando houver uma decisão explícita de reconstruir a base.

O projeto já tem `indexar_base.py` na raiz. Para executar pelo gerenciador, escolha **3 — Indexar/sincronizar a base ChromaDB** e confirme a operação. Também pode executar manualmente da raiz (com Ollama e modelo local disponíveis):

```powershell
.\.venv\Scripts\python.exe indexar_base.py
```

Se o `.venv` não existir, use `python indexar_base.py` no ambiente onde as dependências do projeto estejam instaladas. Não apague `data/chroma_db/` como tentativa genérica de corrigir erros.

## Inicialização manual (sem gerenciador)

Abra três terminais separados:

**Terminal 1 — Ollama** (só se o serviço ainda não estiver ativo):

```powershell
ollama serve
```

Verifique/baixe o modelo uma vez:

```powershell
ollama list
ollama pull nomic-embed-text
```

**Terminal 2 — FastAPI, na raiz do projeto:**

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --host 127.0.0.1 --port 8000
```

**Terminal 3 — Next.js:**

```powershell
cd frontend
npm run dev
```

Abra <http://localhost:3000>. Para desenvolvimento no próprio computador, prefira `localhost`, não `http://192.168.x.x:3000`, porque APIs do navegador e WebSocket/HMR podem falhar em HTTP servido pelo IP local.

## Problemas frequentes

### `Failed to connect to Ollama`

Abra o Ollama, confirme `curl http://127.0.0.1:11434/api/tags` e verifique `ollama list`. Se o modelo faltar, execute `ollama pull nomic-embed-text`.

### Frontend mostra erro genérico e FastAPI retorna 500

Leia o traceback na janela do FastAPI. `/health` pode responder 200 mesmo quando a recuperação RAG ou a chamada ao modelo falha.

### FastAPI retorna 401

Compare `GURAI_API_KEY` e `GURAI_BACKEND_API_KEY` em memória ou com uma ferramenta local; precisam ser iguais. Não imprima nem compartilhe as chaves.

### Frontend informa backend não configurado / 503

Confira `GURAI_BACKEND_URL=http://127.0.0.1:8000` e `GURAI_BACKEND_API_KEY`. Depois de modificar `.env.local`, pare e reinicie `npm run dev`.

### `npm error ENOENT ... package.json`

O comando foi executado fora da pasta `frontend/`. Execute `cd frontend` antes de `npm run dev`, ou use a opção 4 do gerenciador.

### Erro Firebase/Firestore ou autenticação

Confira o projeto Firebase, as credenciais ADC/conta de serviço, permissões no Firestore e configuração de Google OAuth/NextAuth. Não é necessário deixar o Console do Firebase aberto.

## Segurança e limites

- Este kit é um iniciador local para Windows, não um instalador universal nem um serviço de produção.
- Os valores secretos devem ser fornecidos pelo responsável do projeto; nenhum segredo é incluído.
- O modo de desenvolvimento (`npm run dev`) deve ser usado localmente. Para exposição externa, configure autenticação, URLs de callback OAuth e permissões antes de abrir um túnel.
- O acesso público via Cloudflare Tunnel é opcional e não é iniciado automaticamente por este gerenciador.
- O servidor, o computador e a conexão precisam ficar ligados durante a demonstração.
