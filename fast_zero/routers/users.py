from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from fast_zero.models import User
from fast_zero.schemas.user import UserList, UserPublic, UserSchema
from fast_zero.types.index import T_CurrentUser, T_Session
from fast_zero.utils.security import get_password_hash

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", status_code=HTTPStatus.OK, response_model=UserList)
async def read_users(session: T_Session, skip: int = 0, limit: int = 100):
    users = (
        await session.scalars(select(User).offset(skip).limit(limit))
    ).all()
    return {"users": users}


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(
    user: UserSchema,
    session: T_Session,
):
    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Username already exists",
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Email already exists",
            )

    db_user = User(
        username=user.username,
        password=await get_password_hash(user.password),
        email=user.email,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.put("/{user_id}", status_code=HTTPStatus.OK, response_model=UserPublic)
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
