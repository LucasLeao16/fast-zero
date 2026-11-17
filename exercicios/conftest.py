"""Fixtures dos testes dos exercícios.

Reaproveita todas as fixtures de tests/conftest.py (client, session,
user, other_user, token...). Veja docs/EXERCICIOS.md.
"""

import pytest

from tests.conftest import *  # noqa: F403


@pytest.fixture
def auth(token):
    """Header de autenticação do usuário da fixture `user`."""
    return {"Authorization": f"Bearer {token}"}
