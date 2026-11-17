"""Exercício 06: filtro ?created_after=AAAA-MM-DD."""

from datetime import datetime
from http import HTTPStatus

from sqlalchemy import update

from fast_zero.models import Todo
from tests.conftest import TodoFactory


async def test_filtra_por_data_de_criacao(session, client, user, auth):
    todos = TodoFactory.create_batch(3, user_id=user.id)
    session.add_all(todos)
    await session.commit()

    # Dois todos "antigos": mudamos a data direto no banco
    antigos = [todos[0].id, todos[1].id]
    await session.execute(
        update(Todo)
        .where(Todo.id.in_(antigos))
        .values(created_at=datetime(2020, 1, 1))
    )
    await session.commit()

    response = await client.get(
        "/todos/?created_after=2025-01-01", headers=auth
    )

    assert response.status_code == HTTPStatus.OK
    ids = [todo["id"] for todo in response.json()["todos"]]
    assert ids == [todos[2].id]


async def test_data_invalida_retorna_422(client, auth):
    response = await client.get("/todos/?created_after=ontem", headers=auth)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
