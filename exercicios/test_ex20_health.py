"""Exercício 20: GET /health verificando o banco."""

from http import HTTPStatus

from sqlalchemy.exc import OperationalError

from fast_zero.app import app
from fast_zero.database import get_session


async def test_tudo_ok(client):
    response = await client.get("/health")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok", "database": "ok"}


class SessaoQuebrada:
    """Finge um banco fora do ar: qualquer consulta falha."""

    @staticmethod
    async def execute(*args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("banco fora do ar"))


async def test_banco_fora_do_ar_retorna_503(client):
    # A fixture client limpa os overrides ao final do teste
    app.dependency_overrides[get_session] = SessaoQuebrada

    response = await client.get("/health")

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.json() == {"status": "error", "database": "unavailable"}
