"""Exercício 01: GET /todos/{todo_id}."""

from http import HTTPStatus

from tests.conftest import TodoFactory


async def test_retorna_o_todo(session, client, user, auth):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = await client.get(f"/todos/{todo.id}", headers=auth)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["id"] == todo.id
    assert data["title"] == todo.title
    assert data["description"] == todo.description
    assert data["state"] == todo.state


async def test_todo_inexistente_retorna_404(client, auth):
    response = await client.get("/todos/999", headers=auth)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Task not found."}


async def test_todo_de_outro_usuario_retorna_404(
    session, client, other_user, auth
):
    todo = TodoFactory(user_id=other_user.id)
    session.add(todo)
    await session.commit()

    response = await client.get(f"/todos/{todo.id}", headers=auth)

    assert response.status_code == HTTPStatus.NOT_FOUND


async def test_sem_token_retorna_401(client):
    response = await client.get("/todos/1")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
