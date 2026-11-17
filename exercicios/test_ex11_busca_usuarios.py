"""Exercício 11: GET /users/?username=texto."""

from http import HTTPStatus


async def test_busca_parcial_sem_maiusculas(client):
    for username in ["alice", "Alicia", "bob"]:
        await client.post(
            "/users/",
            json={
                "username": username,
                "email": f"{username}@x.com",
                "password": "12345678",
            },
        )

    response = await client.get("/users/?username=ALI")

    assert response.status_code == HTTPStatus.OK
    nomes = [u["username"] for u in response.json()["users"]]
    assert nomes == ["alice", "Alicia"]


async def test_sem_filtro_lista_todos(client, user, other_user):
    response = await client.get("/users/")

    assert len(response.json()["users"]) == 2  # noqa: PLR2004
