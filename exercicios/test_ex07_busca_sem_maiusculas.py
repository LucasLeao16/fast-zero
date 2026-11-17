"""Exercício 07: filtros de texto sem diferenciar maiúsculas."""

from http import HTTPStatus

import pytest

from tests.conftest import TodoFactory


@pytest.mark.parametrize("busca", ["estudar", "PYTHON", "Estudar Python"])
async def test_filtro_de_titulo(session, client, user, auth, busca):
    session.add(TodoFactory(user_id=user.id, title="Estudar Python"))
    session.add(TodoFactory(user_id=user.id, title="Lavar louca"))
    await session.commit()

    response = await client.get(f"/todos/?title={busca}", headers=auth)

    assert response.status_code == HTTPStatus.OK
    titulos = [todo["title"] for todo in response.json()["todos"]]
    assert titulos == ["Estudar Python"]


async def test_filtro_de_descricao(session, client, user, auth):
    session.add(TodoFactory(user_id=user.id, description="Ler a DOCUMENTACAO"))
    await session.commit()

    response = await client.get(
        "/todos/?description=documentacao", headers=auth
    )

    assert len(response.json()["todos"]) == 1
