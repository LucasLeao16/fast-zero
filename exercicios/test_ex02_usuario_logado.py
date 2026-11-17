"""Exercício 02: GET /users/me."""

from http import HTTPStatus


async def test_retorna_o_usuario_logado(client, user, auth):
    response = await client.get("/users/me", headers=auth)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }


async def test_sem_token_retorna_401(client):
    response = await client.get("/users/me")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
