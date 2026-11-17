from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fast_zero.settings import settings

# O engine gerencia o pool de conexões com o banco; é criado uma vez só.
engine = create_async_engine(settings.DATABASE_URL)


async def get_session():  # pragma: no cover
    """Abre uma sessão por requisição e fecha ao final (usada via Depends).

    expire_on_commit=False mantém os objetos utilizáveis depois do commit;
    sem isso, ler um atributo dispararia uma query implícita, o que não é
    permitido em async.
    """
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
