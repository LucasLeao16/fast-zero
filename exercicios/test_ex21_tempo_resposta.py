"""Exercício 21: middleware com o header X-Process-Time."""

import pytest


@pytest.mark.parametrize("rota", ["/", "/users/", "/rota-que-nao-existe"])
async def test_header_em_todas_as_respostas(client, rota):
    response = await client.get(rota)

    assert "X-Process-Time" in response.headers
    assert float(response.headers["X-Process-Time"]) >= 0
