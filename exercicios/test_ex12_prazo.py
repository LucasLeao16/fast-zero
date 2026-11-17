"""Exercício 12: campo opcional due_date (prazo) nos todos."""

from http import HTTPStatus


def novo_todo(**extra):
    return {"title": "t", "description": "d", "state": "todo", **extra}


async def test_criar_com_prazo(client, auth):
    response = await client.post(
        "/todos/", headers=auth, json=novo_todo(due_date="2026-12-31")
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["due_date"] == "2026-12-31"


async def test_prazo_e_opcional(client, auth):
    response = await client.post("/todos/", headers=auth, json=novo_todo())

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["due_date"] is None


async def test_patch_altera_o_prazo(client, auth):
    created = await client.post("/todos/", headers=auth, json=novo_todo())

    response = await client.patch(
        f"/todos/{created.json()['id']}",
        headers=auth,
        json={"due_date": "2027-01-15"},
    )

    assert response.json()["due_date"] == "2027-01-15"


async def test_data_invalida_retorna_422(client, auth):
    response = await client.post(
        "/todos/", headers=auth, json=novo_todo(due_date="31/12/2026")
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
