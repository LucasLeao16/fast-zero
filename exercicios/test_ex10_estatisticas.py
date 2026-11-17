"""Exercício 10: GET /todos/stats."""

from http import HTTPStatus

from fast_zero.models import TodoState
from tests.conftest import TodoFactory


async def test_conta_os_todos_por_estado(
    session, client, user, other_user, auth
):
    session.add_all(
        TodoFactory.create_batch(2, user_id=user.id, state=TodoState.todo)
    )
    session.add(TodoFactory(user_id=user.id, state=TodoState.done))
    # Todos de outro usuário não entram na conta
    session.add(TodoFactory(user_id=other_user.id, state=TodoState.doing))
    await session.commit()

    response = await client.get("/todos/stats", headers=auth)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "draft": 0,
        "todo": 2,
        "doing": 0,
        "done": 1,
        "trash": 0,
    }


async def test_sem_token_retorna_401(client):
    response = await client.get("/todos/stats")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
