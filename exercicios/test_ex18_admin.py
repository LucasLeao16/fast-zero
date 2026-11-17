"""Exercício 18: usuários administradores e GET /admin/todos."""

from http import HTTPStatus

from sqlalchemy import text

from tests.conftest import TodoFactory


async def tornar_admin(session, user):
    await session.execute(
        text("UPDATE users SET is_admin = true WHERE id = :id"),
        {"id": user.id},
    )
    await session.commit()
    # O UPDATE foi direto no banco: o objeto user na memória da sessão
    # ainda tem o valor antigo, então recarregamos
    await session.refresh(user)


async def test_admin_ve_os_todos_de_todos(
    session, client, user, other_user, auth
):
    session.add(TodoFactory(user_id=user.id))
    session.add(TodoFactory(user_id=other_user.id))
    await session.commit()
    await tornar_admin(session, user)

    response = await client.get("/admin/todos", headers=auth)

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["todos"]) == 2  # noqa: PLR2004


async def test_usuario_comum_retorna_403(client, auth):
    response = await client.get("/admin/todos", headers=auth)

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions"}


async def test_novos_usuarios_nao_sao_admin(session, client):
    await client.post(
        "/users/",
        json={"username": "ana", "email": "ana@x.com", "password": "12345678"},
    )

    is_admin = await session.scalar(
        text("SELECT is_admin FROM users WHERE username = 'ana'")
    )

    assert is_admin is False
