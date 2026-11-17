"""Exercício 16: POST /users/me/password."""

from http import HTTPStatus


async def login(client, email, password):
    return await client.post(
        "/auth/token", data={"username": email, "password": password}
    )


async def test_troca_a_senha(client, user, auth):
    response = await client.post(
        "/users/me/password",
        headers=auth,
        json={
            "current_password": user.clean_password,
            "new_password": "senha-nova-123",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Password updated"}
    nova = await login(client, user.email, "senha-nova-123")
    antiga = await login(client, user.email, user.clean_password)
    assert nova.status_code == HTTPStatus.OK
    assert antiga.status_code == HTTPStatus.BAD_REQUEST


async def test_senha_atual_errada_retorna_400(client, user, auth):
    response = await client.post(
        "/users/me/password",
        headers=auth,
        json={"current_password": "errada", "new_password": "senha-nova-123"},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "Incorrect password"}


async def test_sem_token_retorna_401(client):
    response = await client.post(
        "/users/me/password",
        json={"current_password": "a", "new_password": "b"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
