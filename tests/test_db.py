from sqlalchemy import select

from fast_zero.models import Todo, TodoState, User


async def test_create_user(session):
    new_user = User(username="alice", password="secret", email="teste@test")
    session.add(new_user)
    await session.commit()

    user = await session.scalar(select(User).where(User.username == "alice"))

    assert user.username == "alice"


async def test_create_todo(session, user: User):
    todo = Todo(
        title="Test Todo",
        description="Test Desc",
        state=TodoState.draft,
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    # Com expire_on_commit=False o User em memória não é recarregado
    # sozinho; o refresh busca os todos (lazy="selectin") de novo.
    await session.refresh(user)

    assert todo in user.todos
