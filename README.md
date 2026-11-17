# Fast Zero

API de lista de tarefas (todos) com cadastro de usuários e autenticação
JWT, feita para estudo de **FastAPI** com **SQLAlchemy async**,
**PostgreSQL**, **Alembic** e testes com **pytest**.

## Tecnologias

| Para quê | Ferramenta |
|---|---|
| Linguagem | Python 3.14 |
| Framework web | FastAPI |
| Banco de dados | PostgreSQL 18 |
| ORM (async) | SQLAlchemy 2 + psycopg 3 |
| Migrações | Alembic |
| Validação | Pydantic |
| Autenticação | JWT (PyJWT) + hash de senha argon2 (pwdlib) |
| Dependências | uv |
| Testes | pytest, pytest-asyncio, httpx, testcontainers, factory-boy, freezegun |
| Lint/formatação | ruff |

## Estrutura

```
fast_zero/
├── app.py            # cria o FastAPI e registra os routers
├── settings.py       # configurações lidas do .env
├── database.py       # engine e sessão async do banco
├── models.py         # tabelas (User, Todo) e o enum TodoState
├── dependencies.py   # dependências injetadas nas rotas (sessão, usuário logado)
├── routers/          # rotas, uma por recurso
│   ├── auth.py       #   /auth  (login e refresh do token)
│   ├── users.py      #   /users (CRUD de usuários)
│   └── todos.py      #   /todos (CRUD de tarefas do usuário logado)
├── schemas/          # formatos de entrada/saída da API (Pydantic)
└── utils/
    └── security.py   # hash de senha, geração e validação do JWT
migrations/           # migrações do Alembic
tests/                # testes (conftest.py tem as fixtures)
```

> 📘 Para entender como cada parte funciona e para que serve cada
> tecnologia, veja o **[Guia de estudo](docs/GUIA.md)**, com o caminho de
> uma requisição, explicações de cada ferramenta, o mapa dos arquivos e
> exercícios.

**Model x schema:** o *model* (`models.py`) é a tabela no banco; o
*schema* (`schemas/`) é o JSON que entra e sai da API. Eles são separados
para, por exemplo, nunca devolver a senha (`UserPublic` não tem o campo
`password`).

## Configuração

Copie o arquivo de exemplo e ajuste os valores:

```bash
cp .env.example .env
```

Para gerar uma `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Ambiente virtual

O `uv sync` cria o ambiente virtual do projeto na pasta `.venv`, com o
Python e todas as dependências.

**Não é preciso ativá-lo:** o `uv run <comando>` já executa tudo dentro
do `.venv`. Todos os comandos deste README usam essa forma.

Se preferir ativar, para digitar `task test`, `alembic ...` ou `pytest`
sem o prefixo `uv run`, rode dentro da pasta do projeto:

| Terminal | Comando |
|---|---|
| Git Bash | `source .venv/Scripts/activate` |
| PowerShell | `.venv\Scripts\Activate.ps1` |
| CMD | `.venv\Scripts\activate.bat` |
| Linux/macOS | `source .venv/bin/activate` |

Para sair do ambiente: `deactivate`.

No PowerShell, se aparecer um erro dizendo que a execução de scripts
está desabilitada, libere uma vez para o seu usuário:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**VS Code:** selecione o interpretador do projeto em `Ctrl+Shift+P` →
**Python: Select Interpreter** → `.venv`. Assim os terminais novos já
abrem com o ambiente ativo, e o debug usa as mesmas dependências.

## Como rodar

### Tudo no Docker

```bash
docker compose up --build
```

O container da aplicação roda as migrações e sobe a API em
<http://localhost:8000>. A documentação interativa fica em
<http://localhost:8000/docs>.

Para parar: `docker compose down` (adicione `-v` para apagar também os
dados do banco).

### Aplicação local, banco no Docker

Útil durante o desenvolvimento, pois o servidor recarrega a cada
alteração no código:

```bash
uv sync                                    # instala as dependências
docker compose up -d fastzero_database     # sobe só o Postgres
uv run alembic upgrade head                # cria as tabelas
uv run task run                            # fastapi dev (com reload)
```

## Testes e qualidade

```bash
uv run task test     # lint + testes + relatório de cobertura (htmlcov/)
uv run task lint     # lint + verifica a formatação (não altera nada)
uv run task format   # corrige o que der do lint e formata o código
```

Os testes sobem um Postgres temporário via testcontainers, então o
**Docker precisa estar rodando**. O banco do `compose.yaml` não é usado
nem alterado.

## Migrações

Depois de alterar `models.py`:

```bash
uv run alembic revision --autogenerate -m "descrição da mudança"
uv run alembic upgrade head
```

Sempre revise o arquivo gerado em `migrations/versions/`: o
autogenerate não cobre tudo (por exemplo, criar um tipo `ENUM` no
Postgres ou converter dados existentes).

`uv run alembic check` mostra se os models e o banco estão
sincronizados.

## Endpoints

| Método | Rota | Autenticação | Descrição |
|---|---|---|---|
| GET | `/` | — | Olá mundo |
| POST | `/users/` | — | Cria usuário |
| GET | `/users/?offset=0&limit=100` | — | Lista usuários |
| PUT | `/users/{id}` | ✔ | Atualiza o próprio usuário |
| DELETE | `/users/{id}` | ✔ | Remove o próprio usuário (e seus todos) |
| POST | `/auth/token` | — | Login (form: `username` = email, `password`) |
| POST | `/auth/refresh_token` | ✔ | Gera um novo token |
| POST | `/todos/` | ✔ | Cria tarefa |
| GET | `/todos/?title=&description=&state=&offset=&limit=` | ✔ | Lista e filtra tarefas |
| PATCH | `/todos/{id}` | ✔ | Altera campos de uma tarefa |
| DELETE | `/todos/{id}` | ✔ | Remove uma tarefa |

Nas rotas autenticadas, envie o header
`Authorization: Bearer <access_token>`. No `/docs`, use o botão
**Authorize**.

## Conceitos para estudar no código

- **Injeção de dependências** (`dependencies.py`, `Depends`): como cada
  rota recebe a sessão do banco e o usuário logado sem criá-los.
- **async/await** (`database.py`, `routers/`): toda ida ao banco é
  `await`; enquanto espera, o servidor atende outras requisições.
  Trabalho pesado de CPU (hash de senha) vai para uma thread com
  `run_in_threadpool` (`utils/security.py`).
- **Fluxo do JWT** (`utils/security.py`): o login gera um token assinado
  com o email em `sub` e uma expiração em `exp`; a cada requisição,
  `get_current_user` valida a assinatura, a expiração e busca o usuário.
- **Testes isolados** (`tests/conftest.py`): cada teste recebe tabelas
  vazias, e `app.dependency_overrides` troca o banco real pelo de teste.
