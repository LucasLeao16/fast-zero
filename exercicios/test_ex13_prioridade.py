"""Exercício 13: prioridade (low, medium, high) nos todos."""

from http import HTTPStatus


def novo_todo(**extra):
    return {"title": "t", "description": "d", "state": "todo", **extra}


async def test_prioridade_padrao_e_medium(client, auth):
    response = await client.post("/todos/", headers=auth, json=novo_todo())

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["priority"] == "medium"


async def test_criar_com_prioridade(client, auth):
    response = await client.post(
        "/todos/", headers=auth, json=novo_todo(priority="high")
    )

    assert response.json()["priority"] == "high"


async def test_prioridade_invalida_retorna_422(client, auth):
    response = await client.post(
        "/todos/", headers=auth, json=novo_todo(priority="urgente")
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_filtra_por_prioridade(client, auth):
    for priority in ["low", "high", "high"]:
        await client.post(
            "/todos/", headers=auth, json=novo_todo(priority=priority)
        )

    response = await client.get("/todos/?priority=high", headers=auth)

    prioridades = [todo["priority"] for todo in response.json()["todos"]]
    assert prioridades == ["high", "high"]
