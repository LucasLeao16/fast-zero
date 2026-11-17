"""Exercício 08: ?order_by=campo&order=asc|desc."""

from http import HTTPStatus

import pytest

from tests.conftest import TodoFactory


@pytest.fixture
async def todos(session, user):
    # Inseridos fora de ordem alfabética: ids 1, 2, 3 = "b", "a", "c"
    for title in ["b", "a", "c"]:
        session.add(TodoFactory(user_id=user.id, title=title))
        await session.commit()


async def titulos(client, auth, query=""):
    response = await client.get(f"/todos/{query}", headers=auth)
    return [todo["title"] for todo in response.json()["todos"]]


async def test_padrao_continua_por_id(client, auth, todos):
    assert await titulos(client, auth) == ["b", "a", "c"]


async def test_ordena_por_titulo(client, auth, todos):
    assert await titulos(client, auth, "?order_by=title") == ["a", "b", "c"]


async def test_ordena_por_titulo_decrescente(client, auth, todos):
    resultado = await titulos(client, auth, "?order_by=title&order=desc")
    assert resultado == ["c", "b", "a"]


@pytest.mark.parametrize(
    "query", ["?order_by=password", "?order_by=title&order=aleatorio"]
)
async def test_valores_invalidos_retornam_422(client, auth, query):
    response = await client.get(f"/todos/{query}", headers=auth)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
