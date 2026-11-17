"""Exercício 04: título obrigatório e com até 100 caracteres."""

from http import HTTPStatus

import pytest

from tests.conftest import TodoFactory


def novo_todo(title):
    return {"title": title, "description": "d", "state": "todo"}


@pytest.mark.parametrize("title", ["", "a" * 101])
async def test_criar_com_titulo_invalido_retorna_422(client, auth, title):
    response = await client.post(
        "/todos/", headers=auth, json=novo_todo(title)
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("title", ["a", "a" * 100])
async def test_criar_com_titulo_valido_funciona(client, auth, title):
    response = await client.post(
        "/todos/", headers=auth, json=novo_todo(title)
    )

    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.parametrize("title", ["", "a" * 101])
async def test_patch_com_titulo_invalido_retorna_422(
    session, client, user, auth, title
):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = await client.patch(
        f"/todos/{todo.id}", headers=auth, json={"title": title}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
