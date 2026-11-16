from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.dependencies import T_CurrentUser, T_Session
from fast_zero.models import User
from fast_zero.schemas.filter import FilterPage
from fast_zero.schemas.user import UserList, UserPublic, UserSchema
from fast_zero.utils.security import get_password_hash

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UserList)
async def read_users(session: T_Session, page: Annotated[FilterPage, Query()]):
    query = (
        select(User).order_by(User.id).offset(page.offset).limit(page.limit)
    )
    users = (await session.scalars(query)).all()

    return {"users": users}


async def ensure_username_and_email_available(
    session: AsyncSession, user: UserSchema, ignore_user_id: int | None = None
):
    """Levanta 400 se o username ou o email já pertencem a outro usuário.

    `ignore_user_id` permite que o próprio usuário mantenha seus dados
    ao atualizar o cadastro.
    """
    query = select(User).where(
        (User.username == user.username) | (User.email == user.email)
    )

    if ignore_user_id:
        query = query.where(User.id != ignore_user_id)

    db_user = await session.scalar(query)

    if not db_user:
        return

    if db_user.username == user.username:
        detail = "Username already exists"
    else:
        detail = "Email already exists"

    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=detail)


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(
    user: UserSchema,
    session: T_Session,
):
    await ensure_username_and_email_available(session, user)

    db_user = User(
        username=user.username,
        password=await get_password_hash(user.password),
        email=user.email,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.put("/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Not enough permissions",
        )

    await ensure_username_and_email_available(
        session, user, ignore_user_id=current_user.id
    )

    current_user.username = user.username
    current_user.password = await get_password_hash(user.password)
    current_user.email = user.email
    await session.commit()
    await session.refresh(current_user)

    return current_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
        )

    await session.delete(current_user)
    await session.commit()

    return {"message": "User deleted"}
