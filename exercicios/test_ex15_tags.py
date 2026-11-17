"""Exercício 15 (desafio): tags com relacionamento muitos-para-muitos."""

from http import HTTPStatus

from sqlalchemy import text


def novo_todo(**extra):
    return {"title": "t", "description": "d", "state": "todo", **extra}


async def test_criar_com_tags(client, auth):
    response = await client.post(
        "/todos/", headers=auth, json=novo_todo(tags=["python", "estudo"])
    )

    assert response.status_code == HTTPStatus.CREATED
    # As tags voltam em ordem alfabética
    assert response.json()["tags"] == ["estudo", "python"]


async def test_tags_sao_opcionais(client, auth):
    response = await client.post("/todos/", headers=auth, json=novo_todo())

    assert response.json()["tags"] == []


async def test_tags_com_mesmo_nome_sao_reaproveitadas(session, client, auth):
    await client.post("/todos/", headers=auth, json=novo_todo(tags=["a", "b"]))
    await client.post("/todos/", headers=auth, json=novo_todo(tags=["b", "c"]))

    total = await session.scalar(text("SELECT count(*) FROM tags"))

    assert total == 3  # a, b, c  # noqa: PLR2004


async def test_filtra_por_tag(client, auth):
    await client.post("/todos/", headers=auth, json=novo_todo(tags=["casa"]))
    estudo = await client.post(
        "/todos/", headers=auth, json=novo_todo(tags=["estudo", "casa"])
    )

    response = await client.get("/todos/?tag=estudo", headers=auth)

    assert [t["id"] for t in response.json()["todos"]] == [estudo.json()["id"]]


async def test_patch_substitui_as_tags(client, auth):
    created = await client.post(
        "/todos/", headers=auth, json=novo_todo(tags=["a", "b"])
    )

    response = await client.patch(
        f"/todos/{created.json()['id']}", headers=auth, json={"tags": ["c"]}
    )

    assert response.json()["tags"] == ["c"]
