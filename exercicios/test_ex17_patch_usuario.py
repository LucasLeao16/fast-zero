"""Exercício 17: PATCH /users/{user_id} (atualização parcial)."""

from http import HTTPStatus


async def test_altera_so_o_username(client, user, auth):
    response = await client.patch(
        f"/users/{user.id}", headers=auth, json={"username": "novo_nome"}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": user.id,
        "username": "novo_nome",
        "email": user.email,
    }


async def test_altera_a_senha(client, user, auth):
    await client.patch(
        f"/users/{user.id}", headers=auth, json={"password": "outra-senha"}
    )

    response = await client.post(
        "/auth/token",
        data={"username": user.email, "password": "outra-senha"},
    )

    assert response.status_code == HTTPStatus.OK


async def test_email_invalido_retorna_422(client, user, auth):
    response = await client.patch(
        f"/users/{user.id}", headers=auth, json={"email": "nao-e-email"}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_username_de_outro_usuario_retorna_400(
    client, user, other_user, auth
):
    response = await client.patch(
        f"/users/{user.id}",
        headers=auth,
        json={"username": other_user.username},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "Username already exists"}


async def test_outro_usuario_retorna_403(client, other_user, auth):
    response = await client.patch(
        f"/users/{other_user.id}", headers=auth, json={"username": "x"}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
