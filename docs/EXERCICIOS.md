# Exercícios

25 exercícios práticos, em 5 níveis, para estudar o projeto alterando o
código. Cada um passa por várias camadas: rota, schema, model, banco e
testes.

As respostas comentadas estão em [RESPOSTAS.md](RESPOSTAS.md). Tente
resolver antes de olhar!

## Como usar

1. Leia o **objetivo** e o **comportamento esperado**: é a especificação
   do que a API deve fazer quando você terminar.
2. Implemente.
3. Rode o teste do exercício. Cada um tem um arquivo pronto em
   `exercicios/`, que funciona como correção automática:

   ```bash
   uv run pytest exercicios/test_ex01_detalhe_todo.py
   ```

   Antes de você resolver, o teste falha. Quando passar, o exercício está
   certo.
4. Rode também os testes do projeto (`uv run task test`). Às vezes a
   mudança quebra um teste antigo, e **isso faz parte do exercício**:
   entender por que quebrou e ajustar.
5. Se travar, abra a **dica**. Se travar de novo, veja a resposta.

**Observações:**

- Os testes de `exercicios/` **não** rodam no `task test` nem no CI
  (veja `testpaths` no `pyproject.toml`). Rode-os explicitamente.
- Os exercícios são independentes: dá para fazer em qualquer ordem,
  salvo quando o enunciado indicar outra coisa. Mesmo assim, a ordem
  sugerida vai do mais simples ao mais complexo.
- Os exercícios do Nível 3 criam migrações: o banco precisa estar
  rodando (`docker compose up -d fastzero_database`). Os testes não
  precisam disso, porque usam um banco temporário.
- Sugestão: faça cada exercício numa branch (`git checkout -b ex01`).
  Assim fica fácil comparar, desfazer ou recomeçar.

## Índice

| Nº | Exercício | Você vai praticar |
|---|---|---|
| | **Nível 1: rotas e schemas** | |
| 01 | [Detalhe de um todo](#01-detalhe-de-um-todo) | rota com parâmetro no caminho, reaproveitar função |
| 02 | [Usuário logado](#02-usuário-logado) | dependências, `response_model` |
| 03 | [Senha mínima](#03-senha-mínima) | validação com `Field` |
| 04 | [Validação do título](#04-validação-do-título) | validação na entrada **e** na saída |
| 05 | [Datas na resposta](#05-datas-na-resposta) | schema de saída, `server_default`, `onupdate` |
| | **Nível 2: queries** | |
| 06 | [Filtro por data](#06-filtro-por-data) | filtros com `where`, tipo `date` |
| 07 | [Busca sem diferenciar maiúsculas](#07-busca-sem-diferenciar-maiúsculas) | `ILIKE` |
| 08 | [Ordenação](#08-ordenação) | `order_by`, `Literal` |
| 09 | [Total na paginação](#09-total-na-paginação) | `COUNT(*)`, subconsulta |
| 10 | [Estatísticas por estado](#10-estatísticas-por-estado) | `GROUP BY`, ordem das rotas |
| 11 | [Busca de usuários](#11-busca-de-usuários) | herança de schemas de filtro |
| | **Nível 3: models e migrações** | |
| 12 | [Prazo](#12-prazo) | coluna nova, migração, dataclasses |
| 13 | [Prioridade](#13-prioridade) | `Enum`, `server_default`, migração editada à mão |
| 14 | [Lixeira](#14-lixeira) | regra de negócio, `DELETE` em massa, testes frágeis |
| 15 | [Tags (desafio)](#15-tags-desafio) | relacionamento muitos-para-muitos |
| | **Nível 4: autenticação e segurança** | |
| 16 | [Trocar a senha](#16-trocar-a-senha) | verificação de senha, hash |
| 17 | [Atualização parcial de usuário](#17-atualização-parcial-de-usuário) | `PATCH`, campos opcionais |
| 18 | [Administradores](#18-administradores) | dependência que depende de outra, 403 |
| 19 | [Login em tempo constante](#19-login-em-tempo-constante) | ataque de temporização, *monkeypatch* |
| | **Nível 5: async, testes e infraestrutura** | |
| 20 | [Health check](#20-health-check) | tratamento de erro, status 503 |
| 21 | [Tempo de resposta](#21-tempo-de-resposta) | middleware |
| 22 | [Bloqueando o event loop](#22-bloqueando-o-event-loop) | async na prática (experimento) |
| 23 | [Teste da exclusão em cascata](#23-teste-da-exclusão-em-cascata) | escrever um teste do zero |
| 24 | [Cobertura mínima](#24-cobertura-mínima) | pytest-cov, CI |
| 25 | [Tarefas de migração](#25-tarefas-de-migração) | taskipy |

---

## Nível 1: rotas e schemas

### 01. Detalhe de um todo

**Objetivo:** criar `GET /todos/{todo_id}`, que devolve um todo do
usuário logado.

**Comportamento esperado:**

```http
GET /todos/1
Authorization: Bearer <token>
```

| Situação | Status | Corpo |
|---|---|---|
| O todo existe e é do usuário | 200 | o todo, no formato `TodoPublic` |
| Não existe | 404 | `{"detail": "Task not found."}` |
| Existe, mas é de **outro** usuário | 404 | `{"detail": "Task not found."}` |
| Sem token | 401 | |

**Arquivos:** `fast_zero/routers/todos.py`

**Teste:** `uv run pytest exercicios/test_ex01_detalhe_todo.py`

<details>
<summary>Dica</summary>

A função `get_user_todo()` já busca o todo do usuário e levanta 404. A
rota nova fica com uma linha.

Por que devolver 404, e não 403, para o todo de outro usuário? Pense no
que um 403 revelaria.

</details>

### 02. Usuário logado

**Objetivo:** criar `GET /users/me`, que devolve os dados de quem está
logado.

**Comportamento esperado:**

| Situação | Status | Corpo |
|---|---|---|
| Com token | 200 | `{"id": 1, "username": "...", "email": "..."}` |
| Sem token | 401 | |

**Arquivos:** `fast_zero/routers/users.py`

**Teste:** `uv run pytest exercicios/test_ex02_usuario_logado.py`

<details>
<summary>Dica</summary>

A dependência `T_CurrentUser` já entrega o usuário. Não precisa de
nenhuma query. E qual `response_model` garante que a senha não vá junto?

</details>

### 03. Senha mínima

**Objetivo:** exigir senha com pelo menos 8 caracteres no cadastro
(`POST /users/`) e na atualização (`PUT /users/{id}`).

**Comportamento esperado:**

| Senha | Status |
|---|---|
| `"1234567"` (7 caracteres) | 422 |
| `"12345678"` (8 caracteres) | 201 no cadastro |

**Arquivos:** `fast_zero/schemas/user.py`

**Teste:** `uv run pytest exercicios/test_ex03_senha_minima.py`

> ⚠️ Um teste antigo do projeto vai quebrar. Descubra qual e por quê.

<details>
<summary>Dica</summary>

`Field(min_length=...)` do Pydantic. Como os dois endpoints usam o mesmo
schema, uma linha resolve os dois.

</details>

### 04. Validação do título

**Objetivo:** o título do todo passa a ser obrigatório (não pode ser
vazio) e ter no máximo 100 caracteres, tanto ao criar quanto no `PATCH`.

**Comportamento esperado:**

| Título | `POST /todos/` | `PATCH /todos/{id}` |
|---|---|---|
| `""` | 422 | 422 |
| 101 caracteres | 422 | 422 |
| 1 a 100 caracteres | 201 | 200 |

**Arquivos:** `fast_zero/schemas/todo.py`

**Teste:** `uv run pytest exercicios/test_ex04_validacao_titulo.py`

> ⚠️ Depois da mudança, rode `uv run task test` algumas vezes. Alguns
> testes antigos podem falhar com um erro de **validação da resposta**.
> Por que a resposta seria validada?

<details>
<summary>Dica</summary>

Olhe de quem o `TodoPublic` herda. E veja como a `TodoFactory`
(`tests/conftest.py`) gera os títulos e qual o tamanho deles.

</details>

### 05. Datas na resposta

**Objetivo:** incluir `created_at` e `updated_at` nas respostas de
todos.

**Comportamento esperado:**

```json
{
  "id": 1,
  "title": "Estudar",
  "description": "...",
  "state": "todo",
  "created_at": "2026-11-16T20:00:00",
  "updated_at": null
}
```

- Ao criar, `updated_at` é `null`.
- Depois de um `PATCH`, `updated_at` passa a ter a data da alteração.
- A listagem (`GET /todos/`) também traz as duas datas.

**Arquivos:** `fast_zero/schemas/todo.py`

**Teste:** `uv run pytest exercicios/test_ex05_datas_na_resposta.py`

<details>
<summary>Dica</summary>

As colunas já existem no model. Quem preenche cada uma? Procure
`server_default` e `onupdate` em `models.py`.

</details>

---

## Nível 2: queries

### 06. Filtro por data

**Objetivo:** filtrar os todos criados a partir de uma data:
`GET /todos/?created_after=2026-01-01`.

**Comportamento esperado:**

- Devolve só os todos com `created_at` maior ou igual à data.
- Data em formato inválido (`?created_after=ontem`) → 422.
- Funciona junto com os outros filtros.

**Arquivos:** `fast_zero/schemas/todo.py` (`FilterTodo`) e
`fast_zero/routers/todos.py` (`list_todos`)

**Teste:** `uv run pytest exercicios/test_ex06_filtro_data.py`

<details>
<summary>Dica</summary>

Declarar o campo como `date | None` faz o Pydantic validar o formato
sozinho. Na query, é mais um `if` com `.where(...)`.

</details>

### 07. Busca sem diferenciar maiúsculas

**Objetivo:** hoje `?title=estudar` **não** encontra "Estudar Python".
Faça os filtros `title` e `description` ignorarem maiúsculas e
minúsculas.

**Comportamento esperado:**

| Busca | Encontra "Estudar Python"? |
|---|---|
| `?title=estudar` | sim |
| `?title=PYTHON` | sim |
| `?title=Estudar Python` | sim (já funcionava) |

**Arquivos:** `fast_zero/routers/todos.py`

**Teste:** `uv run pytest exercicios/test_ex07_busca_sem_maiusculas.py`

<details>
<summary>Dica</summary>

No SQL, dá para comparar tudo em minúsculas (ou usar `ILIKE`). O
SQLAlchemy tem um método parecido com o
`contains` atual.

</details>

### 08. Ordenação

**Objetivo:** permitir que o cliente escolha a ordem da listagem:
`GET /todos/?order_by=title&order=desc`.

**Comportamento esperado:**

- `order_by` aceita `id`, `title`, `state` e `created_at`. O padrão é
  `id`, como hoje.
- `order` aceita `asc` (padrão) e `desc`.
- Qualquer outro valor → 422. Exemplo: `?order_by=password` não pode
  funcionar!

**Arquivos:** `fast_zero/schemas/todo.py` e `fast_zero/routers/todos.py`

**Teste:** `uv run pytest exercicios/test_ex08_ordenacao.py`

<details>
<summary>Dica</summary>

`Literal["id", "title", ...]` restringe os valores aceitos. Para
transformar o texto `"title"` na coluna `Todo.title`, pesquise
`getattr`.

Por que é perigoso aceitar qualquer nome de coluna vindo do cliente?

</details>

### 09. Total na paginação

**Objetivo:** a listagem de todos passa a informar o total de
resultados, para o cliente saber quantas páginas existem.

**Comportamento esperado:**

```json
{"todos": [...], "total": 5}
```

- `total` conta os todos que passam nos filtros, **ignorando**
  `offset` e `limit`.
- Com 5 todos e `?limit=2`: 2 itens em `todos` e `"total": 5`.
- Sem nenhum todo: `{"todos": [], "total": 0}`.

**Arquivos:** `fast_zero/schemas/todo.py` (`TodoList`) e
`fast_zero/routers/todos.py`

**Teste:** `uv run pytest exercicios/test_ex09_total_paginacao.py`

<details>
<summary>Dica</summary>

Conte **antes** de aplicar `offset` e `limit`. A query filtrada pode
virar uma subconsulta:
`select(func.count()).select_from(query.subquery())`.

</details>

### 10. Estatísticas por estado

**Objetivo:** criar `GET /todos/stats`, com quantos todos o usuário tem
em cada estado.

**Comportamento esperado:**

```json
{"draft": 0, "todo": 2, "doing": 0, "done": 1, "trash": 0}
```

- Todos os estados aparecem, mesmo os que estão em zero.
- Só conta os todos do usuário logado.
- Sem token → 401.

**Arquivos:** `fast_zero/routers/todos.py`

**Teste:** `uv run pytest exercicios/test_ex10_estatisticas.py`

> ⚠️ Se você fez o exercício 01, `GET /todos/stats` pode responder 422.
> Por quê?

<details>
<summary>Dica</summary>

`select(Todo.state, func.count()).group_by(Todo.state)`. Estados sem
nenhum todo não aparecem no resultado do `GROUP BY`: complete com zero
percorrendo `TodoState`.

Sobre o 422: o FastAPI testa as rotas **na ordem em que foram
declaradas**.

</details>

### 11. Busca de usuários

**Objetivo:** buscar usuários pelo nome: `GET /users/?username=ali`.

**Comportamento esperado:**

- Busca parcial e sem diferenciar maiúsculas: `ALI` encontra "alice" e
  "Alicia".
- Sem o filtro, lista todos, como hoje.
- A paginação (`offset`/`limit`) continua funcionando.

**Arquivos:** `fast_zero/schemas/user.py` e `fast_zero/routers/users.py`

**Teste:** `uv run pytest exercicios/test_ex11_busca_usuarios.py`

<details>
<summary>Dica</summary>

Crie um `FilterUser` que herda de `FilterPage`, do jeito que o
`FilterTodo` faz.

</details>

---

## Nível 3: models e migrações

### 12. Prazo

**Objetivo:** adicionar um prazo opcional, `due_date`, aos todos.

**Comportamento esperado:**

- `POST /todos/` aceita `"due_date": "2026-12-31"`; sem o campo, fica
  `null`.
- As respostas incluem `due_date`.
- O `PATCH` altera o prazo.
- Data inválida (`"31/12/2026"`) → 422.
- Existe uma migração nova, e `uv run alembic check` não acusa
  diferenças.

**Arquivos:** `fast_zero/models.py`, `fast_zero/schemas/todo.py`,
`fast_zero/routers/todos.py` e uma migração nova

**Teste:** `uv run pytest exercicios/test_ex12_prazo.py`

<details>
<summary>Dica</summary>

1. Coluna no model: `Mapped[date | None]` com `default=None`. Atenção:
   em dataclasses, campos com valor padrão precisam vir **depois** dos
   obrigatórios.
2. Gere a migração: `uv run alembic revision --autogenerate -m "..."`.
   Revise o arquivo e aplique com `uv run alembic upgrade head`.
3. Inclua o campo nos schemas e no `Todo(...)` da rota de criação.

</details>

### 13. Prioridade

**Objetivo:** adicionar uma prioridade aos todos: `low`, `medium` ou
`high`.

**Comportamento esperado:**

- Sem informar, a prioridade é `medium`.
- Valor inválido (`"urgente"`) → 422.
- Filtro `GET /todos/?priority=high`.
- Os todos que **já existem** no banco ficam com `medium` depois da
  migração.

**Arquivos:** `fast_zero/models.py`, `fast_zero/schemas/todo.py`,
`fast_zero/routers/todos.py` e uma migração nova

**Teste:** `uv run pytest exercicios/test_ex13_prioridade.py`

> ⚠️ Rode a migração gerada **sem editar** primeiro e leia o erro. O
> autogenerate não faz tudo sozinho aqui.

<details>
<summary>Dica</summary>

Crie um `TodoPriority(StrEnum)` como o `TodoState`. A coluna precisa de
`default` (para o Python) e de `server_default` (para o banco preencher
as linhas antigas).

Na migração, o tipo `ENUM` precisa ser criado no Postgres antes da
coluna. Veja como a migração `e36ad7ab3e8e` fez isso.

</details>

### 14. Lixeira

**Objetivo:** a exclusão passa a ter duas etapas, como a lixeira do
computador.

**Comportamento esperado:**

| Requisição | Situação | Resposta |
|---|---|---|
| `DELETE /todos/{id}` | o todo **não** está na lixeira | muda o estado para `trash`: `{"message": "Task moved to trash."}` |
| `DELETE /todos/{id}` | o todo **já está** na lixeira | apaga de vez: `{"message": "Task has been deleted successfully."}` |
| `DELETE /todos/trash` | | apaga todos os todos do usuário que estão na lixeira: `{"deleted": 2}` |
| `GET /todos/` | sem filtro de estado | **não** mostra os da lixeira |
| `GET /todos/?state=trash` | | mostra só os da lixeira |

A lixeira de um usuário nunca afeta a de outro.

**Arquivos:** `fast_zero/routers/todos.py`

**Teste:** `uv run pytest exercicios/test_ex14_lixeira.py`

> ⚠️ Depois da mudança, rode `uv run task test` **várias vezes**. Testes
> antigos vão falhar, e nem sempre os mesmos! Descubra a causa
> (`tests/conftest.py` tem a pista).

<details>
<summary>Dica</summary>

- Para esvaziar a lixeira, `delete(Todo).where(...)` apaga direto no
  banco. Para saber quantos foram apagados, pesquise `.returning()`.
- `DELETE /todos/trash` e `DELETE /todos/{todo_id}`: qual deve ser
  declarada primeiro?
- Sobre os testes aleatórios: como a `TodoFactory` escolhe o estado?

</details>

### 15. Tags (desafio)

**Objetivo:** permitir etiquetar os todos com tags. Uma tag pode estar
em vários todos, e um todo pode ter várias tags: é um relacionamento
**muitos-para-muitos**.

**Comportamento esperado:**

- `POST /todos/` aceita `"tags": ["python", "estudo"]` (opcional; sem o
  campo, `[]`).
- As respostas trazem `"tags": ["estudo", "python"]`: só os nomes, em
  ordem alfabética.
- Tags com o mesmo nome são reaproveitadas: existe **uma** linha por nome
  na tabela `tags`.
- `GET /todos/?tag=estudo` filtra pelos todos que têm a tag.
- `PATCH` com `"tags": [...]` **substitui** a lista inteira.
- Tabelas: `tags` (`id`, `name` único) e `todo_tags` (`todo_id`,
  `tag_id`).

**Arquivos:** `fast_zero/models.py`, `fast_zero/schemas/todo.py`,
`fast_zero/routers/todos.py` e uma migração nova

**Teste:** `uv run pytest exercicios/test_ex15_tags.py`

<details>
<summary>Dica</summary>

1. A tabela de associação `todo_tags` pode ser uma `Table` simples, sem
   classe. No `Todo`, use `relationship(secondary=todo_tags, ...)`.
   Lembre do `lazy="selectin"` (por que ele é necessário?).
2. No banco, `todo.tags` é uma lista de objetos `Tag`; na API, uma
   lista de textos. Um `field_validator(..., mode="before")` no
   `TodoPublic` faz a conversão.
3. Crie uma função que recebe os nomes e devolve os objetos `Tag`,
   buscando os que já existem e criando os que faltam.
4. Filtro: `Todo.tags.any(Tag.name == ...)`.
5. Para a exclusão de um todo também limpar a `todo_tags`, pesquise
   `ondelete="CASCADE"`.

</details>

---

## Nível 4: autenticação e segurança

### 16. Trocar a senha

**Objetivo:** criar `POST /users/me/password`, que troca a senha do
usuário logado, exigindo a senha atual.

**Comportamento esperado:**

```json
{"current_password": "senha-atual", "new_password": "senha-nova-123"}
```

| Situação | Status | Corpo |
|---|---|---|
| Senha atual correta | 200 | `{"message": "Password updated"}` |
| Senha atual errada | 400 | `{"detail": "Incorrect password"}` |
| Sem token | 401 | |

Depois da troca, o login funciona com a senha nova e **não** funciona
mais com a antiga.

**Arquivos:** `fast_zero/schemas/user.py` e `fast_zero/routers/users.py`

**Teste:** `uv run pytest exercicios/test_ex16_trocar_senha.py`

<details>
<summary>Dica</summary>

`verify_password` e `get_password_hash` (com `await`) já existem em
`utils/security.py`. Se o token já prova quem é o usuário, por que pedir
a senha atual?

</details>

### 17. Atualização parcial de usuário

**Objetivo:** criar `PATCH /users/{user_id}`. Diferente do `PUT`, que
exige todos os campos, o `PATCH` altera só os campos enviados.

**Comportamento esperado:**

- `{"username": "novo"}` altera só o username; email e senha continuam
  iguais.
- `{"password": "..."}` troca a senha (com hash, e no mínimo 8
  caracteres se você fez o exercício 03).
- Email inválido → 422.
- Username ou email que já pertence a outro usuário → 400, com as
  mesmas mensagens do cadastro.
- Alterar outro usuário → 403.

**Arquivos:** `fast_zero/schemas/user.py` e `fast_zero/routers/users.py`

**Teste:** `uv run pytest exercicios/test_ex17_patch_usuario.py`

<details>
<summary>Dica</summary>

- Schema com todos os campos opcionais (`str | None = None`) e
  `model_dump(exclude_unset=True)`, como no `PATCH` de todos.
- A função `ensure_username_and_email_available` recebe um
  `UserSchema` completo. Como reaproveitá-la quando só um dos campos foi
  enviado?
- E se o cliente mandar `{"username": null}`?

</details>

### 18. Administradores

**Objetivo:** criar usuários administradores e uma rota que só eles
podem usar: `GET /admin/todos`, que lista os todos de **todos** os
usuários.

**Comportamento esperado:**

- Nova coluna `users.is_admin` (booleana, padrão `false`), com migração.
- Admin → 200 com `{"todos": [...]}`.
- Usuário comum → 403 `{"detail": "Not enough permissions"}`.
- Usuários novos **não** são admin.
- Não há rota para virar admin: isso é feito direto no banco, de
  propósito.

**Arquivos:** `fast_zero/models.py`, `fast_zero/routers/admin.py` (novo),
`fast_zero/app.py` e uma migração nova

**Teste:** `uv run pytest exercicios/test_ex18_admin.py`

<details>
<summary>Dica</summary>

Crie uma dependência `get_admin_user` que recebe o `T_CurrentUser` e
levanta 403 se ele não for admin. Dependências podem depender de outras
dependências.

Para tornar-se admin no banco local:
`UPDATE users SET is_admin = true WHERE email = '...';`

</details>

### 19. Login em tempo constante

**Objetivo:** hoje, quando o email não existe, o login responde na hora.
Quando existe, ele calcula o hash argon2, que é lento de propósito.
Medindo o tempo de resposta, um atacante descobre quais emails estão
cadastrados, mesmo com a mensagem de erro sendo a mesma. Corrija isso.

**Comportamento esperado:**

- O login **sempre** chama `verify_password`, uma única vez, inclusive
  quando o email não existe.
- Quando o email não existe, a verificação usa um hash argon2 de
  verdade, para gastar o mesmo tempo.
- As respostas continuam iguais: 400 `Incorrect email or password`.

**Arquivos:** `fast_zero/utils/security.py` e `fast_zero/routers/auth.py`

**Teste:** `uv run pytest exercicios/test_ex19_login_tempo_constante.py`

O teste usa *monkeypatch* para trocar o `verify_password` por um
"espião" que registra as chamadas. Vale ler o teste para entender a
técnica.

<details>
<summary>Dica</summary>

Calcule uma vez, quando o módulo é carregado, o hash de uma senha
qualquer. Use-o quando o usuário não existir.

</details>

---

## Nível 5: async, testes e infraestrutura

### 20. Health check

**Objetivo:** criar `GET /health`, que diz se a API está no ar e
consegue falar com o banco.

**Comportamento esperado:**

| Situação | Status | Corpo |
|---|---|---|
| Banco respondendo | 200 | `{"status": "ok", "database": "ok"}` |
| Banco fora do ar | 503 | `{"status": "error", "database": "unavailable"}` |

**Arquivos:** `fast_zero/routers/health.py` (novo) e `fast_zero/app.py`

**Teste:** `uv run pytest exercicios/test_ex20_health.py`

O teste simula o banco fora do ar com uma sessão "quebrada", usando
`dependency_overrides`. Vale ler.

<details>
<summary>Dica</summary>

- A consulta mais simples possível: `await session.execute(text("SELECT 1"))`.
- Os erros de banco do SQLAlchemy herdam de `SQLAlchemyError`.
- Para mudar o status da resposta sem levantar exceção, receba
  `response: Response` como parâmetro.

</details>

### 21. Tempo de resposta

**Objetivo:** toda resposta da API passa a ter o header
`X-Process-Time`, com o tempo de processamento em segundos.

**Comportamento esperado:**

- O header está em **todas** as respostas, inclusive nos erros 404 de
  rotas que não existem.
- O valor é um número maior ou igual a zero, como `0.0123`.

**Arquivos:** `fast_zero/app.py`

**Teste:** `uv run pytest exercicios/test_ex21_tempo_resposta.py`

<details>
<summary>Dica</summary>

Pesquise `@app.middleware("http")`. Para medir tempo, use
`time.perf_counter()`.

</details>

### 22. Bloqueando o event loop

**Objetivo:** ver na prática o que significa bloquear o event loop.
Este exercício é um **experimento**, sem teste automático.

**Passos:**

1. Crie três rotas temporárias em `app.py`:
   - `async def` com `time.sleep(1)`;
   - `async def` com `await asyncio.sleep(1)`;
   - `def` (sem `async`) com `time.sleep(1)`.
2. Suba a API com `uv run fastapi run fast_zero/app.py`.
3. Faça 5 requisições **simultâneas** em cada rota e meça o tempo
   total. No Git Bash:

   ```bash
   time (for i in 1 2 3 4 5; do curl -s localhost:8000/sua-rota > /dev/null & done; wait)
   ```

4. Compare os três tempos e tente explicar cada um.
5. Apague as rotas.

**Comportamento esperado:** uma das rotas leva cerca de 5 segundos; as
outras duas, cerca de 1 segundo. Antes de rodar, tente adivinhar qual é
qual.

<details>
<summary>Dica</summary>

O `time.sleep` "segura" a thread onde está rodando. Em qual thread roda
uma rota `async def`? E uma rota `def`?

</details>

### 23. Teste da exclusão em cascata

**Objetivo:** ao excluir um usuário, os todos dele também são excluídos
(`cascade` em `models.py`), mas nenhum teste verifica isso. Escreva esse
teste em `tests/test_users.py`.

**Comportamento esperado:**

- O teste cria um usuário com alguns todos, exclui o usuário pela API e
  confere, consultando o banco, que os todos sumiram.
- O teste **passa** com o código atual.
- O teste **falha** se você remover `cascade="all, delete-orphan"` de
  `User.todos`. Experimente! Um teste que não falha quando o código
  quebra não testa nada.

Este exercício não tem teste automático: o teste é o exercício.

<details>
<summary>Dica</summary>

Se o teste falhar com `ForeignKeyViolation` mesmo com a cascata no
lugar, você caiu numa armadilha clássica de testes com SQLAlchemy.
Pense: nos testes, todas as requisições usam a **mesma** sessão. Quando o
objeto `user` foi carregado, ele tinha quantos todos?

</details>

### 24. Cobertura mínima

**Objetivo:** fazer o `task test` falhar se a cobertura de testes ficar
abaixo de um mínimo. Assim, o CI barra código novo sem teste.

**Comportamento esperado:**

- A tarefa `test` do taskipy usa a opção `--cov-fail-under`.
- Com a cobertura abaixo do mínimo, o `task test` falha com
  `FAIL Required test coverage of N% not reached`.

**Arquivos:** `pyproject.toml`

**Teste:** `uv run pytest exercicios/test_ex24_cobertura_minima.py`

> ⚠️ Pense no valor: se você já fez outros exercícios, o código deles é
> testado em `exercicios/`, que o `task test` não roda.

<details>
<summary>Dica</summary>

Rode `uv run task test` e veja a cobertura atual no relatório.

</details>

### 25. Tarefas de migração

**Objetivo:** criar atalhos no taskipy para as migrações.

**Comportamento esperado:**

- `task migrate` roda `alembic upgrade head`.
- `task makemigrations "descrição"` roda
  `alembic revision --autogenerate -m "descrição"`.

**Arquivos:** `pyproject.toml`

**Teste:** `uv run pytest exercicios/test_ex25_tarefas_migracao.py`

<details>
<summary>Dica</summary>

O taskipy repassa ao comando os argumentos digitados depois do nome da
tarefa.

</details>
