# Respostas dos exercícios

Respostas comentadas dos [exercícios](EXERCICIOS.md). Tente resolver
antes de ler!

Cada resposta mostra só o que muda em relação ao projeto original, com
os imports necessários. Todas foram validadas: com a resposta aplicada,
o teste do exercício e os testes do projeto passam.

Não existe uma única solução certa. Se o seu código é diferente e os
testes passam, ótimo! Compare as duas versões e veja qual é mais
legível.

## Sumário

**Nível 1:**
[01](#01-detalhe-de-um-todo) ·
[02](#02-usuário-logado) ·
[03](#03-senha-mínima) ·
[04](#04-validação-do-título) ·
[05](#05-datas-na-resposta)

**Nível 2:**
[06](#06-filtro-por-data) ·
[07](#07-busca-sem-diferenciar-maiúsculas) ·
[08](#08-ordenação) ·
[09](#09-total-na-paginação) ·
[10](#10-estatísticas-por-estado) ·
[11](#11-busca-de-usuários)

**Nível 3:**
[12](#12-prazo) ·
[13](#13-prioridade) ·
[14](#14-lixeira) ·
[15](#15-tags-desafio)

**Nível 4:**
[16](#16-trocar-a-senha) ·
[17](#17-atualização-parcial-de-usuário) ·
[18](#18-administradores) ·
[19](#19-login-em-tempo-constante)

**Nível 5:**
[20](#20-health-check) ·
[21](#21-tempo-de-resposta) ·
[22](#22-bloqueando-o-event-loop) ·
[23](#23-teste-da-exclusão-em-cascata) ·
[24](#24-cobertura-mínima) ·
[25](#25-tarefas-de-migração)

---

## Nível 1: rotas e schemas

### 01. Detalhe de um todo

<details>
<summary>Ver resposta</summary>

Em `fast_zero/routers/todos.py`, depois da função `get_user_todo`:

```python
@router.get("/{todo_id}", response_model=TodoPublic)
async def read_todo(todo_id: int, user: T_CurrentUser, session: T_Session):
    return await get_user_todo(session, user.id, todo_id)
```

**Por que funciona:** o `get_user_todo` já filtra por
`Todo.user_id == user_id`. O todo de outro usuário simplesmente "não
existe" para essa query, e cai no 404.

**Por que 404 e não 403:** um 403 ("você não tem permissão") confirmaria
que o todo existe. Com 404, quem tenta adivinhar ids não descobre nada.

**Atenção ao futuro:** se depois você criar `GET /todos/stats`
(exercício 10), declare essa rota **antes** desta. Veja a explicação
lá.

</details>

### 02. Usuário logado

<details>
<summary>Ver resposta</summary>

Em `fast_zero/routers/users.py`:

```python
@router.get("/me", response_model=UserPublic)
async def read_me(current_user: T_CurrentUser):
    return current_user
```

**Por que funciona:** a dependência `T_CurrentUser` valida o token e
busca o usuário. A rota só devolve o objeto, e o
`response_model=UserPublic` garante que a senha fique de fora.

Aqui não há conflito de rotas porque não existe `GET /users/{user_id}`.
Se existisse, `/me` precisaria ser declarada antes, pelo mesmo motivo do
exercício 10.

</details>

### 03. Senha mínima

<details>
<summary>Ver resposta</summary>

Em `fast_zero/schemas/user.py`:

```python
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8)
```

**O teste que quebra:** `test_create_user`, em `tests/test_users.py`,
cadastra um usuário com a senha `"secret"` (6 caracteres) e passa a
receber 422. A regra mudou, então o teste precisa mudar junto:

```python
"password": "secret123",
```

Esse é o papel dos testes: quando uma regra muda, eles mostram tudo que
dependia da regra antiga.

</details>

### 04. Validação do título

<details>
<summary>Ver resposta</summary>

Em `fast_zero/schemas/todo.py`:

```python
from pydantic import BaseModel, Field


class TodoSchema(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    ...


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    ...
```

**A armadilha:** depois dessa mudança, testes antigos de listagem falham
com `ResponseValidationError: String should have at most 100 characters`.
Dois detalhes se juntam:

1. O `TodoPublic` **herda** do `TodoSchema`, então herda também a regra
   dos 100 caracteres. O FastAPI valida a **resposta** com o
   `response_model`, não só a entrada.
2. A `TodoFactory` gera títulos com `Faker("text")`, que produz textos
   de até 200 caracteres. Como a factory grava direto no banco, o
   título passa sem validação na entrada e só é barrado na saída.

**Correção nos testes** (`tests/conftest.py`): títulos de verdade são
curtos, e a factory deve refletir isso:

```python
title = factory.Faker("sentence")  # frase curta: cabe nos 100 caracteres
```

**Lição:** regras de validação valem para a entrada **e** para a saída
quando os schemas são herdados. Em produção, isso importa: se o banco
tivesse títulos antigos com mais de 100 caracteres, de antes da regra,
listá-los passaria a dar erro 500. Duas saídas possíveis: uma migração
que ajusta os dados antigos, ou um schema de saída que não herda as
regras de entrada.

</details>

### 05. Datas na resposta

<details>
<summary>Ver resposta</summary>

Em `fast_zero/schemas/todo.py`:

```python
from datetime import datetime


class TodoPublic(TodoSchema):
    id: int
    created_at: datetime
    updated_at: datetime | None
```

**Quem preenche as datas** (`models.py`):

- `created_at` tem `server_default=func.now()`: o **banco** preenche na
  inserção. O `session.refresh()` da rota de criação busca o valor de
  volta.
- `updated_at` tem `onupdate=func.now()`: o SQLAlchemy inclui
  `updated_at = now()` em todo `UPDATE`. Por isso ele é `null` na
  criação e ganha valor no primeiro `PATCH`.

**O teste que quebra:** `test_create_todo` compara o JSON inteiro, e as
datas mudam a cada execução. A solução é conferir que elas existem e
tirá-las do dicionário antes de comparar:

```python
data = response.json()
# As datas mudam a cada execução: confere que existem e tira do dict
assert data.pop("created_at")
assert data.pop("updated_at") is None
assert data == {
    "id": 1,
    "title": "Test todo",
    ...
}
```

</details>

---

## Nível 2: queries

### 06. Filtro por data

<details>
<summary>Ver resposta</summary>

Em `fast_zero/schemas/todo.py`:

```python
from datetime import date


class FilterTodo(FilterPage):
    ...
    created_after: date | None = None
```

Em `fast_zero/routers/todos.py`, dentro de `list_todos`, junto com os
outros filtros:

```python
if filters.created_after:
    query = query.where(Todo.created_at >= filters.created_after)
```

**Por que funciona:** o tipo `date` faz o Pydantic aceitar só o formato
`AAAA-MM-DD` e responder 422 para o resto. No banco, o Postgres compara
o `timestamp` com a data considerando a meia-noite.

</details>

### 07. Busca sem diferenciar maiúsculas

<details>
<summary>Ver resposta</summary>

Em `fast_zero/routers/todos.py`, troque `contains` por `icontains`:

```python
if filters.title:
    query = query.where(Todo.title.icontains(filters.title))

if filters.description:
    query = query.where(Todo.description.icontains(filters.description))
```

**O que muda no SQL:** `contains` gera `title LIKE '%estudar%'`, que
diferencia maiúsculas. `icontains` gera
`lower(title) LIKE lower('%estudar%')`, que não diferencia.

Dá para ver o SQL de qualquer query com `print(query)`.

</details>

### 08. Ordenação

<details>
<summary>Ver resposta</summary>

Em `fast_zero/schemas/todo.py`:

```python
from typing import Literal


class FilterTodo(FilterPage):
    ...
    order_by: Literal["id", "title", "state", "created_at"] = "id"
    order: Literal["asc", "desc"] = "asc"
```

Em `fast_zero/routers/todos.py`, no lugar do `order_by(Todo.id)`:

```python
# getattr(Todo, "title") é o mesmo que Todo.title
column = getattr(Todo, filters.order_by)
order = column.desc() if filters.order == "desc" else column.asc()

query = query.order_by(order).offset(filters.offset).limit(filters.limit)
```

**Por que o `Literal` é essencial:** sem ele, o cliente poderia mandar
`?order_by=password`, ou o nome de qualquer atributo do model.
Ordenar por senha permitiria descobrir informações sobre os hashes
comparando posições. Com o `Literal`, o Pydantic só aceita os valores
listados e responde 422 para o resto. **Nunca** use texto vindo do
cliente para escolher colunas sem uma lista do que é permitido.

</details>

### 09. Total na paginação

<details>
<summary>Ver resposta</summary>

Em `fast_zero/schemas/todo.py`:

```python
class TodoList(BaseModel):
    todos: list[TodoPublic]
    total: int
```

Em `fast_zero/routers/todos.py`:

```python
from sqlalchemy import func, select
```

Em `list_todos`, **depois** dos filtros e **antes** do
`order_by`/`offset`/`limit`:

```python
# Conta antes de paginar: o total considera os filtros, mas não o
# offset/limit. A query filtrada vira uma subconsulta do COUNT(*).
total = await session.scalar(
    select(func.count()).select_from(query.subquery())
)
```

E no retorno:

```python
return {"todos": todos, "total": total}
```

**O SQL gerado:**

```sql
SELECT count(*) FROM (
    SELECT ... FROM todos WHERE user_id = 1 AND title LIKE '%alfa%'
) AS anon_1
```

Reaproveitar a mesma `query` como subconsulta garante que o total use
exatamente os mesmos filtros da listagem.

</details>

### 10. Estatísticas por estado

<details>
<summary>Ver resposta</summary>

Em `fast_zero/routers/todos.py`:

```python
from sqlalchemy import func, select

from fast_zero.models import Todo, TodoState
```

```python
# Precisa vir ANTES de GET /{todo_id}: o FastAPI testa as rotas na ordem
# em que foram declaradas, e "/stats" casaria com "/{todo_id}".
@router.get("/stats")
async def todo_stats(user: T_CurrentUser, session: T_Session):
    query = (
        select(Todo.state, func.count())
        .where(Todo.user_id == user.id)
        .group_by(Todo.state)
    )
    counts = dict((await session.execute(query)).all())

    # Estados sem nenhum todo não aparecem no GROUP BY: completamos com 0
    return {state.value: counts.get(state, 0) for state in TodoState}
```

**O 422 do aviso:** com o exercício 01 feito, existe
`GET /todos/{todo_id}`. Se ela for declarada antes de `/stats`, o
FastAPI tenta encaixar `"stats"` como `todo_id`, não consegue converter
para `int` e responde 422. A ordem de declaração importa sempre que uma
rota fixa e uma com parâmetro "competem" pelo mesmo caminho.

**Como funciona o `dict(...)`:** cada linha do resultado é uma tupla
`(estado, quantidade)`, e `dict()` transforma a lista de tuplas em
`{estado: quantidade}`.

</details>

### 11. Busca de usuários

<details>
<summary>Ver resposta</summary>

Em `fast_zero/schemas/user.py`:

```python
from fast_zero.schemas.filter import FilterPage


class FilterUser(FilterPage):
    username: str | None = None
```

Em `fast_zero/routers/users.py`, troque o `FilterPage` por `FilterUser`
nos imports e reescreva a rota:

```python
@router.get("/", response_model=UserList)
async def read_users(
    session: T_Session, filters: Annotated[FilterUser, Query()]
):
    query = select(User)

    if filters.username:
        query = query.where(User.username.icontains(filters.username))

    query = query.order_by(User.id).offset(filters.offset).limit(filters.limit)
    users = (await session.scalars(query)).all()

    return {"users": users}
```

**Por que herdar:** o `FilterUser` ganha `offset` e `limit`, com as
mesmas validações, sem repetir código. É o mesmo padrão do `FilterTodo`.

</details>

---

## Nível 3: models e migrações

### 12. Prazo

<details>
<summary>Ver resposta</summary>

**Model** (`fast_zero/models.py`):

```python
from datetime import date, datetime


class Todo:
    ...
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # Campos com valor padrão vêm depois dos obrigatórios (regra das
    # dataclasses). "date | None" vira uma coluna DATE que aceita nulo.
    due_date: Mapped[date | None] = mapped_column(default=None)

    user: Mapped[User] = relationship(init=False, back_populates="todos")
```

Se você colocar o `due_date` antes do `user_id`, o Python reclama:
`non-default argument 'user_id' follows default argument`. É a mesma
regra das funções: em `def f(a=1, b)`, o `b` não pode vir depois.

**Schemas** (`fast_zero/schemas/todo.py`):

```python
from datetime import date


class TodoSchema(BaseModel):
    ...
    due_date: date | None = None


class TodoUpdate(BaseModel):
    ...
    due_date: date | None = None
```

O `TodoPublic` herda o campo do `TodoSchema`.

**Rota de criação** (`fast_zero/routers/todos.py`): inclua o campo no
`Todo(...)`:

```python
db_todo = Todo(
    title=todo.title,
    description=todo.description,
    state=todo.state,
    user_id=user.id,
    due_date=todo.due_date,
)
```

**Migração:**

```bash
uv run alembic revision --autogenerate -m "add due_date to todos"
uv run alembic upgrade head
uv run alembic check
```

O arquivo gerado já está correto: uma coluna opcional é o caso mais
simples para o autogenerate.

```python
def upgrade() -> None:
    op.add_column("todos", sa.Column("due_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("todos", "due_date")
```

**Teste antigo:** `test_create_todo` compara o JSON inteiro. Inclua
`"due_date": None` no dicionário esperado.

</details>

### 13. Prioridade

<details>
<summary>Ver resposta</summary>

**Model** (`fast_zero/models.py`):

```python
class TodoPriority(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"


class Todo:
    ...
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # default: valor usado pelo Python ao criar o objeto;
    # server_default: valor usado pelo banco (inclusive nas linhas que já
    # existiam quando a coluna foi criada pela migração)
    priority: Mapped[TodoPriority] = mapped_column(
        default=TodoPriority.medium, server_default=TodoPriority.medium
    )
```

**Schemas** (`fast_zero/schemas/todo.py`):

```python
from fast_zero.models import TodoPriority, TodoState


class TodoSchema(BaseModel):
    ...
    priority: TodoPriority = TodoPriority.medium


class TodoUpdate(BaseModel):
    ...
    priority: TodoPriority | None = None


class FilterTodo(FilterPage):
    ...
    priority: TodoPriority | None = None
```

**Rota** (`fast_zero/routers/todos.py`): `priority=todo.priority` no
`Todo(...)` e o filtro:

```python
if filters.priority:
    query = query.where(Todo.priority == filters.priority)
```

**Migração: o autogenerate não basta.** O arquivo gerado tenta criar a
coluna direto, e falha:

```
psycopg.errors.UndefinedObject: type "todopriority" does not exist
```

O `add_column` não cria o tipo `ENUM` no Postgres. A versão corrigida:

```python
todopriority = sa.Enum("low", "medium", "high", name="todopriority")


def upgrade() -> None:
    # O add_column não cria o tipo ENUM no Postgres; criamos antes.
    todopriority.create(op.get_bind(), checkfirst=True)
    # server_default preenche as linhas que já existem: sem ele, o
    # NOT NULL falharia em tabelas com dados.
    op.add_column(
        "todos",
        sa.Column(
            "priority",
            todopriority,
            server_default="medium",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("todos", "priority")
    todopriority.drop(op.get_bind(), checkfirst=True)
```

Como a migração falhou dentro de uma transação, o Postgres desfez tudo,
e dá para corrigir o arquivo e rodar de novo. Depois de aplicar, os
todos que já existiam ficam com `medium`. Confira com
`SELECT priority, count(*) FROM todos GROUP BY 1;`.

**Teste antigo:** inclua `"priority": "medium"` no dicionário esperado
de `test_create_todo`.

</details>

### 14. Lixeira

<details>
<summary>Ver resposta</summary>

Em `fast_zero/routers/todos.py`:

```python
from sqlalchemy import delete, select

from fast_zero.models import Todo, TodoState
```

**Listagem:** sem filtro de estado, esconde a lixeira:

```python
if filters.state:
    query = query.where(Todo.state == filters.state)
else:
    # Sem filtro de estado, a lixeira fica escondida
    query = query.where(Todo.state != TodoState.trash)
```

**Esvaziar a lixeira e excluir em duas etapas:**

```python
# Precisa vir ANTES de DELETE /{todo_id}, pelo mesmo motivo de /stats
@router.delete("/trash")
async def empty_trash(user: T_CurrentUser, session: T_Session):
    # delete() apaga direto no banco, sem carregar os objetos na memória.
    # returning() faz o banco devolver os ids apagados (DELETE ... RETURNING)
    deleted_ids = (
        await session.scalars(
            delete(Todo)
            .where(Todo.user_id == user.id, Todo.state == TodoState.trash)
            .returning(Todo.id)
        )
    ).all()
    await session.commit()

    return {"deleted": len(deleted_ids)}


@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, user: T_CurrentUser, session: T_Session):
    db_todo = await get_user_todo(session, user.id, todo_id)

    # 1ª exclusão: vai para a lixeira. 2ª exclusão: remove de vez.
    if db_todo.state != TodoState.trash:
        db_todo.state = TodoState.trash
        await session.commit()
        return {"message": "Task moved to trash."}

    await session.delete(db_todo)
    await session.commit()

    return {"message": "Task has been deleted successfully."}
```

**Os testes aleatórios:** a `TodoFactory` sorteia o estado entre
**todos** os valores, inclusive `trash`. Um teste que cria 5 todos e
espera 5 na listagem passa a falhar sempre que algum é sorteado como
`trash`. Isso acontece às vezes, em testes diferentes a cada execução.
Testes que falham aleatoriamente ("flaky") são piores do que testes que
sempre falham, porque minam a confiança na suíte.

A correção (`tests/conftest.py`):

```python
# Sorteia qualquer estado menos "trash": todos na lixeira não aparecem
# na listagem padrão, e isso deixaria os testes aleatórios
state = factory.fuzzy.FuzzyChoice([
    state for state in TodoState if state != TodoState.trash
])
```

E `test_delete_todo` passa a esperar
`{"message": "Task moved to trash."}`, porque o todo da factory nunca
começa na lixeira.

**`delete()` x `session.delete()`:** o `session.delete(obj)` apaga um
objeto já carregado e respeita as cascatas do ORM. O `delete(Todo)` gera
um `DELETE ... WHERE` direto no banco: é mais rápido para muitas linhas,
mas não carrega nada na memória.

</details>

### 15. Tags (desafio)

<details>
<summary>Ver resposta</summary>

**Models** (`fast_zero/models.py`):

```python
from sqlalchemy import Column, ForeignKey, Table, func

# Tabela de associação do muitos-para-muitos: cada linha liga um todo a
# uma tag. Não precisa de classe, porque não tem dados próprios.
# ondelete="CASCADE": se o todo ou a tag for apagado, o vínculo também é.
todo_tags = Table(
    "todo_tags",
    table_registry.metadata,
    Column(
        "todo_id", ForeignKey("todos.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    ),
)


@table_registry.mapped_as_dataclass
class Tag:
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
```

No `Todo`, depois dos campos obrigatórios:

```python
    # secondary: o relacionamento passa pela tabela todo_tags
    tags: Mapped[list[Tag]] = relationship(
        secondary=todo_tags, lazy="selectin", default_factory=list
    )
```

- `lazy="selectin"`: como em `User.todos`, em async não há
  carregamento implícito, então as tags vêm junto com o todo.
- `ondelete="CASCADE"` importa para o "esvaziar a lixeira" do exercício
  14: aquele `delete()` em massa não passa pelo ORM, então é o
  **banco** que precisa limpar a `todo_tags`.

**Schemas** (`fast_zero/schemas/todo.py`):

```python
from pydantic import BaseModel, Field, field_validator


class TodoSchema(BaseModel):
    ...
    tags: list[str] = []


class TodoPublic(TodoSchema):
    ...

    # No banco, todo.tags é uma lista de objetos Tag; na API, só os nomes.
    # mode="before" roda antes da validação do tipo list[str].
    @field_validator("tags", mode="before")
    @classmethod
    def tag_names(cls, tags):
        return sorted(getattr(tag, "name", tag) for tag in tags)


class TodoUpdate(BaseModel):
    ...
    tags: list[str] | None = None


class FilterTodo(FilterPage):
    ...
    tag: str | None = None
```

**Rotas** (`fast_zero/routers/todos.py`):

```python
from fast_zero.models import Tag, Todo


async def get_or_create_tags(session: AsyncSession, names: list[str]):
    """Devolve as tags com esses nomes, criando as que ainda não existem."""
    names = sorted(set(names))  # remove repetidos
    existing = (
        await session.scalars(select(Tag).where(Tag.name.in_(names)))
    ).all()
    existing_names = {tag.name for tag in existing}
    new_tags = [Tag(name=name) for name in names if name not in existing_names]

    return [*existing, *new_tags]
```

Na criação, `tags=await get_or_create_tags(session, todo.tags)` dentro
do `Todo(...)`. No filtro:

```python
if filters.tag:
    # any(): existe pelo menos uma tag do todo com esse nome
    query = query.where(Todo.tags.any(Tag.name == filters.tag))
```

No `PATCH`, as tags precisam de tratamento à parte, porque os nomes
precisam virar objetos:

```python
# exclude_unset: só os campos enviados no JSON são alterados
data = todo.model_dump(exclude_unset=True)

# tags é um relacionamento: os nomes precisam virar objetos Tag
if "tags" in data:
    db_todo.tags = await get_or_create_tags(session, data.pop("tags"))

for key, value in data.items():
    setattr(db_todo, key, value)
```

**Migração:** o autogenerate cria as duas tabelas corretamente, com as
chaves estrangeiras e o `ondelete`. Tabelas novas são um caso que ele
cobre bem.

**Teste antigo:** inclua `"tags": []` no dicionário esperado de
`test_create_todo`.

</details>

---

## Nível 4: autenticação e segurança

### 16. Trocar a senha

<details>
<summary>Ver resposta</summary>

Em `fast_zero/schemas/user.py`:

```python
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
```

Em `fast_zero/routers/users.py`:

```python
from fast_zero.utils.security import get_password_hash, verify_password


@router.post("/me/password")
async def change_password(
    passwords: PasswordChange, current_user: T_CurrentUser, session: T_Session
):
    # Pedir a senha atual protege contra quem pegou um token emprestado
    # (ou um computador desbloqueado) de trocar a senha da vítima
    if not await verify_password(
        passwords.current_password, current_user.password
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Incorrect password"
        )

    current_user.password = await get_password_hash(passwords.new_password)
    await session.commit()

    return {"message": "Password updated"}
```

**Por que pedir a senha atual:** o token só prova que *alguém* tem
acesso à sessão. Pode ser alguém que achou o computador desbloqueado ou
que roubou o token. Sem a senha atual, essa pessoa trocaria a senha e
tomaria a conta.

</details>

### 17. Atualização parcial de usuário

<details>
<summary>Ver resposta</summary>

**Schema** (`fast_zero/schemas/user.py`):

```python
class UserUpdate(BaseModel):
    """Todos os campos opcionais: o PATCH altera só o que for enviado."""

    username: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)
```

**Reaproveitando a checagem:** a `ensure_username_and_email_available`
recebia um `UserSchema` completo. Para servir ao `PATCH`, ela passa a
receber só os dois valores:

```python
async def ensure_username_and_email_available(
    session: AsyncSession,
    username: str,
    email: str,
    ignore_user_id: int | None = None,
):
    ...
    query = select(User).where(
        (User.username == username) | (User.email == email)
    )
    ...
    if db_user.username == username:
        detail = "Username already exists"
```

As chamadas existentes mudam para
`ensure_username_and_email_available(session, user.username, user.email)`
(com `ignore_user_id=current_user.id` no `PUT`).

**A rota:**

```python
@router.patch("/{user_id}", response_model=UserPublic)
async def patch_user(
    user_id: int,
    user: UserUpdate,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
        )

    # exclude_none: em usuários nenhum campo pode ser nulo, então um
    # {"username": null} enviado é ignorado em vez de virar erro no banco
    data = user.model_dump(exclude_unset=True, exclude_none=True)

    # Campo não enviado = mantém o valor atual (é ele que vai para a checagem)
    await ensure_username_and_email_available(
        session,
        data.get("username", current_user.username),
        data.get("email", current_user.email),
        ignore_user_id=current_user.id,
    )

    if "password" in data:
        data["password"] = await get_password_hash(data["password"])

    for key, value in data.items():
        setattr(current_user, key, value)

    await session.commit()
    await session.refresh(current_user)

    return current_user
```

**`exclude_unset` x `exclude_none`:**

- `exclude_unset=True` descarta os campos que o cliente **não enviou**.
- `exclude_none=True` descarta também os que ele enviou como `null`.
  Sem isso, `{"username": null}` tentaria gravar `NULL` numa coluna
  `NOT NULL`, e a API responderia 500.

No `PATCH` de todos não usamos `exclude_none`, porque lá um `null` pode
ser intencional, como em `"due_date": null` para remover o prazo.

</details>

### 18. Administradores

<details>
<summary>Ver resposta</summary>

**Model** (`fast_zero/models.py`), no final da classe `User`:

```python
from sqlalchemy import false

    is_admin: Mapped[bool] = mapped_column(
        default=False, server_default=false()
    )
```

O `server_default=false()` preenche os usuários que já existem quando a
migração roda. O autogenerate gera a migração correta:

```python
op.add_column(
    "users",
    sa.Column(
        "is_admin",
        sa.Boolean(),
        server_default=sa.text("false"),
        nullable=False,
    ),
)
```

**Router novo** (`fast_zero/routers/admin.py`):

```python
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from fast_zero.dependencies import T_CurrentUser, T_Session
from fast_zero.models import Todo, User
from fast_zero.schemas.todo import TodoList

router = APIRouter(prefix="/admin", tags=["admin"])


def get_admin_user(user: T_CurrentUser) -> User:
    """Dependência que só deixa passar administradores (senão, 403)."""
    if not user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
        )
    return user


# Uma dependência pode depender de outra: get_admin_user usa T_CurrentUser,
# que por sua vez usa a sessão e o token
T_AdminUser = Annotated[User, Depends(get_admin_user)]


@router.get("/todos", response_model=TodoList)
async def list_all_todos(admin: T_AdminUser, session: T_Session):
    todos = (await session.scalars(select(Todo).order_by(Todo.id))).all()

    return {"todos": todos, "total": len(todos)}
```

O `"total"` é para o caso de você ter feito o exercício 09. Se não fez,
o Pydantic simplesmente ignora a chave extra.

**Registrar o router** (`fast_zero/app.py`):

```python
from fast_zero.routers import admin, auth, todos, users

app.include_router(admin.router)
```

**Uma armadilha no teste:** o teste torna o usuário admin com um
`UPDATE` direto no banco e depois chama `session.refresh(user)`. Sem o
refresh, o objeto `user` na memória da sessão continuaria com
`is_admin = False`. Como os testes usam a mesma sessão em todas as
requisições, a API leria esse valor antigo. O exercício 23 volta a esse
assunto.

</details>

### 19. Login em tempo constante

<details>
<summary>Ver resposta</summary>

Em `fast_zero/utils/security.py`:

```python
pwd_context = PasswordHash.recommended()

# Hash de uma senha qualquer, calculado uma vez só. O login o usa quando o
# email não existe, para gastar o mesmo tempo de quando o email existe.
DUMMY_PASSWORD_HASH = pwd_context.hash("senha-que-ninguem-usa")
```

Em `fast_zero/routers/auth.py`:

```python
from fast_zero.utils.security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    verify_password,
)
```

```python
    # A senha é SEMPRE verificada, mesmo sem usuário. Sem isso, um email
    # inexistente responderia bem mais rápido (sem o cálculo do argon2) e
    # o tempo de resposta revelaria quais emails estão cadastrados.
    password_hash = user.password if user else DUMMY_PASSWORD_HASH
    password_ok = await verify_password(form_data.password, password_hash)

    # A mesma mensagem nos dois casos evita revelar quais emails existem
    if not user or not password_ok:
        raise HTTPException(...)
```

**O problema original:** o código fazia `not user or not verify(...)`.
Pelo curto-circuito do `or`, quando `user` é `None` o `verify` nem roda.
A resposta saía em milissegundos, contra dezenas de milissegundos do
argon2. Isso é um **ataque de temporização** (*timing attack*): mesmo
com mensagens iguais, o tempo entrega a informação.

**Sobre o teste:** o *monkeypatch* troca o `verify_password` **dentro de
`fast_zero.routers.auth`**, que é onde ele é usado. Como o `auth.py`
importa o nome direto (`from ... import verify_password`), trocar em
`fast_zero.utils.security` não teria efeito no router.

</details>

---

## Nível 5: async, testes e infraestrutura

### 20. Health check

<details>
<summary>Ver resposta</summary>

Router novo (`fast_zero/routers/health.py`):

```python
from http import HTTPStatus

from fastapi import APIRouter, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from fast_zero.dependencies import T_Session

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(session: T_Session, response: Response):
    """Diz se a API está no ar e consegue falar com o banco.

    Ferramentas de monitoramento (e o healthcheck do Docker) chamam esta
    rota de tempos em tempos.
    """
    try:
        # A consulta mais simples possível: só prova que o banco responde
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        # Receber o Response como parâmetro permite mudar o status
        response.status_code = HTTPStatus.SERVICE_UNAVAILABLE
        return {"status": "error", "database": "unavailable"}

    return {"status": "ok", "database": "ok"}
```

E em `fast_zero/app.py`: `app.include_router(health.router)`.

**Por que capturar `SQLAlchemyError` e não `Exception`:** capturar tudo
esconderia bugs do próprio código. Um erro de digitação também viraria
"banco fora do ar". Capture só o que você sabe tratar.

**Indo além:** o `compose.yaml` poderia usar essa rota num
`healthcheck` do serviço da aplicação, assim como já faz com o
`pg_isready` no banco.

</details>

### 21. Tempo de resposta

<details>
<summary>Ver resposta</summary>

Em `fast_zero/app.py`:

```python
import time

from fastapi import FastAPI, Request

app = FastAPI()


# Um middleware envolve TODAS as requisições: o código antes do call_next
# roda na ida, e o depois roda na volta, já com a resposta pronta.
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{elapsed:.4f}"
    return response
```

**Por que `perf_counter` e não `time.time()`:** o `perf_counter` é um
relógio próprio para medir intervalos, com alta precisão, e não muda se
o relógio do sistema for ajustado.

Como o middleware envolve tudo, o header aparece até nos 404 de rotas
que não existem.

</details>

### 22. Bloqueando o event loop

<details>
<summary>Ver resposta</summary>

As três rotas:

```python
import asyncio
import time


@app.get("/exercicio/bloqueante")
async def bloqueante():
    time.sleep(1)  # trava o event loop inteiro por 1 segundo
    return {"ok": True}


@app.get("/exercicio/nao-bloqueante")
async def nao_bloqueante():
    await asyncio.sleep(1)  # libera o event loop enquanto espera
    return {"ok": True}


@app.get("/exercicio/sincrona")
def sincrona():
    time.sleep(1)  # rota "def": o FastAPI a executa numa thread separada
    return {"ok": True}
```

**Resultado medido** (5 requisições simultâneas em cada rota):

| Rota | Tempo total |
|---|---|
| `async def` + `time.sleep(1)` | **5,27 s** |
| `async def` + `await asyncio.sleep(1)` | 1,28 s |
| `def` + `time.sleep(1)` | 1,27 s |

**Explicação:**

- **`async def` + `time.sleep`**: rotas `async def` rodam no event loop,
  que é **uma única thread**. O `time.sleep` trava essa thread, então as
  5 requisições são atendidas uma depois da outra: 5 × 1 s. Durante esse
  tempo, **nenhuma** outra requisição da API é atendida.
- **`async def` + `await asyncio.sleep`**: o `await` devolve o controle
  ao event loop enquanto espera, e as 5 esperas acontecem ao mesmo
  tempo.
- **`def` + `time.sleep`**: o FastAPI percebe que a rota não é `async`
  e a executa numa thread separada (*threadpool*). A espera trava só
  aquela thread.

**A lição:** o pior caso é `async def` com uma chamada bloqueante. O
código *parece* assíncrono, mas trava o servidor. É por isso que o hash
de senha deste projeto usa `run_in_threadpool`: o argon2 é um cálculo
pesado, que bloquearia o event loop como o `time.sleep`.

</details>

### 23. Teste da exclusão em cascata

<details>
<summary>Ver resposta</summary>

Em `tests/test_users.py`:

```python
from sqlalchemy import func, select

from fast_zero.models import Todo
from tests.conftest import TodoFactory


async def test_delete_user_also_deletes_todos(session, client, user, token):
    session.add_all(TodoFactory.create_batch(3, user_id=user.id))
    await session.commit()
    # Nos testes, a sessão é a mesma em todas as requisições e o objeto
    # user foi carregado antes dos todos existirem (user.todos == []).
    # Sem o refresh, o SQLAlchemy não saberia que há todos para apagar.
    await session.refresh(user)

    response = await client.delete(
        f"/users/{user.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.OK
    remaining = await session.scalar(
        select(func.count()).select_from(Todo).where(Todo.user_id == user.id)
    )
    assert remaining == 0
```

**Validação:** o teste passa com o código atual e **falha** nos dois
cenários errados:

1. Removendo o `cascade="all, delete-orphan"` do model.
2. Removendo o `session.refresh(user)`.

**A armadilha do `refresh`:** sem ele, o teste falha com
`ForeignKeyViolation`, mesmo com a cascata no lugar. O motivo:

1. A fixture `user` carregou o usuário quando ele ainda não tinha
   todos: `user.todos == []`.
2. Os todos foram criados depois, com `user_id=user.id`, mas a lista
   `user.todos` do objeto **na memória** não é atualizada sozinha.
3. Na exclusão, a API busca o usuário e recebe **o mesmo objeto**,
   porque nos testes a sessão é compartilhada e ela reaproveita o que já
   tem na memória (*identity map*). O SQLAlchemy acha que não há todos
   para apagar e tenta apagar só o usuário. O banco recusa, porque ainda
   existem todos apontando para ele.

**Em produção isso não acontece:** cada requisição abre uma sessão
nova, que carrega o usuário e os todos do zero.

**Alternativa mais robusta:** colocar a cascata também no banco, com
`ForeignKey("users.id", ondelete="CASCADE")` em `Todo.user_id` (mais
uma migração) e `passive_deletes=True` no relacionamento. Assim o banco
apaga os todos sozinho, sem depender do que está carregado na memória.

</details>

### 24. Cobertura mínima

<details>
<summary>Ver resposta</summary>

Em `pyproject.toml`:

```toml
test = 'pytest -x --cov=fast_zero --cov-fail-under=100 -vv'
```

Abaixo do mínimo, o `task test` (e o CI) falha:

```
FAIL Required test coverage of 100% not reached. Total coverage: 88.74%
```

**Qual valor usar:** o projeto original tem 100% de cobertura, então
100 é um bom mínimo. Mas pense no aviso do enunciado: o código dos
exercícios é testado em `exercicios/`, que o `task test` não roda. Com
**todos** os exercícios resolvidos, a cobertura medida pelo `task test`
cai para cerca de 89% (foi o número medido nas respostas). Somando os
testes dos exercícios, volta a 100%.

O caminho certo é **mover para `tests/`** os testes dos exercícios que
você resolveu: eles passam a fazer parte do projeto, a rodar no CI e a
proteger o código contra regressões.

</details>

### 25. Tarefas de migração

<details>
<summary>Ver resposta</summary>

Em `pyproject.toml`, na seção `[tool.taskipy.tasks]`:

```toml
migrate = 'alembic upgrade head'
makemigrations = 'alembic revision --autogenerate -m'
```

Uso:

```bash
uv run task migrate
uv run task makemigrations "add due_date to todos"
```

O taskipy repassa ao comando o que vem depois do nome da tarefa, então o
texto entre aspas vira o argumento do `-m`.

</details>
