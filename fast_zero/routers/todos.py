from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.dependencies import T_CurrentUser, T_Session
from fast_zero.models import Todo
from fast_zero.schemas.todo import (
    FilterTodo,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", status_code=HTTPStatus.CREATED, response_model=TodoPublic)
async def create_todo(
    todo: TodoSchema, user: T_CurrentUser, session: T_Session
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )
    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get("/", response_model=TodoList)
async def list_todos(
    session: T_Session,
    user: T_CurrentUser,
    # Query() faz o FastAPI ler os campos do schema da query string:
    # /todos/?title=abc&state=done&limit=10
    filters: Annotated[FilterTodo, Query()],
):
    query = select(Todo).where(Todo.user_id == user.id)

    if filters.title:
        query = query.where(Todo.title.contains(filters.title))

    if filters.description:
        query = query.where(Todo.description.contains(filters.description))

    if filters.state:
        query = query.where(Todo.state == filters.state)

    query = query.order_by(Todo.id).offset(filters.offset).limit(filters.limit)
    todos = (await session.scalars(query)).all()

    return {"todos": todos}


async def get_user_todo(session: AsyncSession, user_id: int, todo_id: int):
    """Busca um todo do usuário ou levanta 404."""
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user_id, Todo.id == todo_id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Task not found."
        )

    return todo


@router.patch("/{todo_id}", response_model=TodoPublic)
async def patch_todo(
    todo_id: int, todo: TodoUpdate, user: T_CurrentUser, session: T_Session
):
    db_todo = await get_user_todo(session, user.id, todo_id)

    # exclude_unset: só os campos enviados no JSON são alterados
    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, user: T_CurrentUser, session: T_Session):
    db_todo = await get_user_todo(session, user.id, todo_id)

    await session.delete(db_todo)
    await session.commit()

    return {"message": "Task has been deleted successfully."}
