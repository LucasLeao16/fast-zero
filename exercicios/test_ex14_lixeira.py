"""Exercício 14: lixeira (exclusão em duas etapas)."""

from http import HTTPStatus

from fast_zero.models import TodoState
from tests.conftest import TodoFactory


async def criar(session, user, state):
    todo = TodoFactory(user_id=user.id, state=state)
    session.add(todo)
    await session.commit()
    return todo


async def test_delete_move_para_a_lixeira(session, client, user, auth):
    todo = await criar(session, user, TodoState.todo)

    response = await client.delete(f"/todos/{todo.id}", headers=auth)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Task moved to trash."}
    lixeira = await client.get("/todos/?state=trash", headers=auth)
    assert [t["id"] for t in lixeira.json()["todos"]] == [todo.id]


async def test_delete_na_lixeira_remove_de_vez(session, client, user, auth):
    todo = await criar(session, user, TodoState.trash)

    response = await client.delete(f"/todos/{todo.id}", headers=auth)

    assert response.json() == {
        "message": "Task has been deleted successfully."
    }
    lixeira = await client.get("/todos/?state=trash", headers=auth)
    assert lixeira.json()["todos"] == []


async def test_listagem_padrao_esconde_a_lixeira(session, client, user, auth):
    visivel = await criar(session, user, TodoState.todo)
    await criar(session, user, TodoState.trash)

    response = await client.get("/todos/", headers=auth)

    assert [t["id"] for t in response.json()["todos"]] == [visivel.id]


async def test_esvaziar_a_lixeira(session, client, user, other_user, auth):
    await criar(session, user, TodoState.trash)
    await criar(session, user, TodoState.trash)
    mantido = await criar(session, user, TodoState.done)
    # A lixeira de outro usuário não é afetada
    await criar(session, other_user, TodoState.trash)

    response = await client.delete("/todos/trash", headers=auth)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"deleted": 2}
    restantes = await client.get("/todos/", headers=auth)
    assert [t["id"] for t in restantes.json()["todos"]] == [mantido.id]
