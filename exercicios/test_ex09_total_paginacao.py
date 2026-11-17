"""Exercício 09: campo "total" na listagem paginada de todos."""

from tests.conftest import TodoFactory


async def test_total_ignora_offset_e_limit(session, client, user, auth):
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = await client.get("/todos/?offset=1&limit=2", headers=auth)

    data = response.json()
    assert len(data["todos"]) == 2  # noqa: PLR2004
    assert data["total"] == 5  # noqa: PLR2004


async def test_total_respeita_os_filtros(session, client, user, auth):
    session.add_all(TodoFactory.create_batch(3, user_id=user.id, title="alfa"))
    session.add_all(TodoFactory.create_batch(2, user_id=user.id, title="beta"))
    await session.commit()

    response = await client.get("/todos/?title=alfa&limit=1", headers=auth)

    data = response.json()
    assert len(data["todos"]) == 1
    assert data["total"] == 3  # noqa: PLR2004


async def test_total_zero_sem_todos(client, auth):
    response = await client.get("/todos/", headers=auth)

    assert response.json() == {"todos": [], "total": 0}
