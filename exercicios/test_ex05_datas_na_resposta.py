"""Exercício 05: created_at e updated_at na resposta dos todos."""

from datetime import datetime
from http import HTTPStatus


async def test_criacao_retorna_created_at_e_updated_at_nulo(client, auth):
    response = await client.post(
        "/todos/",
        headers=auth,
        json={"title": "t", "description": "d", "state": "todo"},
    )

    data = response.json()
    assert isinstance(datetime.fromisoformat(data["created_at"]), datetime)
    assert data["updated_at"] is None


async def test_patch_preenche_updated_at(client, auth):
    created = await client.post(
        "/todos/",
        headers=auth,
        json={"title": "t", "description": "d", "state": "todo"},
    )
    todo_id = created.json()["id"]

    response = await client.patch(
        f"/todos/{todo_id}", headers=auth, json={"title": "novo"}
    )

    assert response.status_code == HTTPStatus.OK
    updated_at = response.json()["updated_at"]
    assert isinstance(datetime.fromisoformat(updated_at), datetime)


async def test_listagem_tambem_retorna_as_datas(client, auth):
    await client.post(
        "/todos/",
        headers=auth,
        json={"title": "t", "description": "d", "state": "todo"},
    )

    response = await client.get("/todos/", headers=auth)

    todo = response.json()["todos"][0]
    assert "created_at" in todo
    assert "updated_at" in todo
