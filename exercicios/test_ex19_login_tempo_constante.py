"""Exercício 19: o login verifica a senha mesmo quando o email não existe."""

from http import HTTPStatus

import pytest


@pytest.fixture
def chamadas(monkeypatch):
    """Troca verify_password por um "espião" que registra as chamadas."""
    registro = []

    async def verify_password_espiao(plain_password, hashed_password):
        registro.append(hashed_password)
        return False

    monkeypatch.setattr(
        "fast_zero.routers.auth.verify_password", verify_password_espiao
    )
    return registro


async def test_email_inexistente_tambem_verifica_senha(client, chamadas):
    response = await client.post(
        "/auth/token",
        data={"username": "ninguem@x.com", "password": "qualquer"},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert len(chamadas) == 1
    # Um hash argon2 de verdade, para o cálculo levar o mesmo tempo
    assert chamadas[0].startswith("$argon2")


async def test_senha_errada_verifica_uma_vez(client, user, chamadas):
    response = await client.post(
        "/auth/token", data={"username": user.email, "password": "errada"}
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert chamadas == [user.password]
