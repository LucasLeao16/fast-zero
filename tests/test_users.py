from http import HTTPStatus

from fast_zero.schemas.user import UserPublic


async def test_read_users(client):
    response = await client.get("/users/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": []}


async def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = await client.get("/users/")
    assert response.json() == {"users": [user_schema]}


async def test_create_user(client):
    response = await client.post(
        "/users/",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "secret",
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "username": "alice",
        "email": "alice@example.com",
        "id": 1,
    }


async def test_create_username_allready_exist(client, user):
    await client.post(
        "/users/",
        json={
            "username": "lucas",
            "email": "lucs@example.com",
            "password": "password",
        },
    )
    response = await client.post(
        "/users/",
        json={
            "username": "lucas",
            "email": "soldier@example.com",
            "password": "password",
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


async def test_create_email_allready_exist(client, user):
    await client.post(
        "/users/",
        json={
            "username": "lucas",
            "email": "lucs@example.com",
            "password": "password",
        },
    )
    response = await client.post(
        "/users/",
        json={
            "username": "Noctis",
            "email": "lucs@example.com",
            "password": "password",
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


async def test_update_user(client, user, token):
    response = await client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "mynewpassword",
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "bob",
        "email": "bob@example.com",
        "id": user.id,
    }


async def test_update_user_with_wrong_user(client, other_user, token):
    response = await client.put(
        f"/users/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "mynewpassword",
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions"}


async def test_delete_user(client, user, token):
    response = await client.delete(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}


async def test_delete_user_wrong_user(client, other_user, token):
    response = await client.delete(
        f"/users/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions"}


async def test_delete_user_not_exist(client, other_user):
    response = await client.delete(f"/users/{other_user.id}")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_update_user_with_existing_username(
    client, user, other_user, token
):
    response = await client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": other_user.username,
            "email": "novo@example.com",
            "password": "mynewpassword",
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "Username already exists"}


async def test_update_user_with_existing_email(
    client, user, other_user, token
):
    response = await client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "novo",
            "email": other_user.email,
            "password": "mynewpassword",
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "Email already exists"}
