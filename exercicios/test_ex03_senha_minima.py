"""Exercício 03: senha com no mínimo 8 caracteres."""

from http import HTTPStatus


async def test_cadastro_com_senha_curta_retorna_422(client):
    response = await client.post(
        "/users/",
        json={"username": "ana", "email": "ana@x.com", "password": "1234567"},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_cadastro_com_8_caracteres_funciona(client):
    response = await client.post(
        "/users/",
        json={"username": "ana", "email": "ana@x.com", "password": "12345678"},
    )

    assert response.status_code == HTTPStatus.CREATED


async def test_atualizacao_com_senha_curta_retorna_422(client, user, auth):
    response = await client.put(
        f"/users/{user.id}",
        headers=auth,
        json={"username": "novo", "email": "novo@x.com", "password": "curta"},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
