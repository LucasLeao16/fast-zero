import asyncio

import factory
import factory.fuzzy
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.community.postgres import PostgresContainer

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import Todo, TodoState, User, table_registry
from fast_zero.utils.security import get_password_hash


def pytest_asyncio_loop_factories(config, item):
    # O psycopg async não funciona com o ProactorEventLoop (padrão no
    # Windows); o SelectorEventLoop funciona em todas as plataformas.
    return {"selector": asyncio.SelectorEventLoop}


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"test{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")
    password = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker("text")
    description = factory.Faker("text")
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


# Sobe um Postgres descartável no Docker uma vez por execução dos testes
@pytest.fixture(scope="session")
def database_url():
    with PostgresContainer("postgres:18", driver="psycopg") as postgres:
        yield postgres.get_connection_url()


@pytest_asyncio.fixture
async def engine(database_url):
    _engine = create_async_engine(database_url)
    yield _engine
    await _engine.dispose()


# Cada teste começa com as tabelas vazias: cria antes e apaga depois
@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def client(session):
    def get_session_override():
        return session

    # Troca a sessão do banco real pela sessão do teste em todas as rotas
    app.dependency_overrides[get_session] = get_session_override

    # ASGITransport chama a aplicação direto, sem abrir um servidor HTTP
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


async def _create_user(session, password):
    user = UserFactory(password=await get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Guarda a senha em texto puro só para os testes poderem fazer login
    user.clean_password = password
    return user


@pytest_asyncio.fixture
async def user(session):
    return await _create_user(session, "testtest")


@pytest_asyncio.fixture
async def other_user(session):
    return await _create_user(session, "testtest")


@pytest_asyncio.fixture
async def token(client, user):
    response = await client.post(
        "/auth/token",
        data={"username": user.email, "password": user.clean_password},
    )
    return response.json()["access_token"]
