from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.settings import settings

pwd_context = PasswordHash.recommended()

# Lê o header "Authorization: Bearer <token>" e informa ao Swagger
# (/docs) em qual rota o login é feito.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_access_token(data: dict) -> str:
    """Gera um JWT assinado com SECRET_KEY e com data de expiração."""
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {**data, "exp": expire}

    return encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# O argon2 é intencionalmente pesado em CPU; rodar numa thread evita
# bloquear o event loop (e as outras requisições) durante o cálculo.
async def get_password_hash(password: str) -> str:
    return await run_in_threadpool(pwd_context.hash, password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return await run_in_threadpool(
        pwd_context.verify, plain_password, hashed_password
    )


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """Valida o token e retorna o usuário dono dele (ou 401)."""
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except (
        InvalidTokenError
    ):  # token malformado, assinatura errada ou expirado
        raise credentials_exception

    email = payload.get("sub")  # "sub" (subject): quem é o dono do token
    if not email:
        raise credentials_exception

    user = await session.scalar(select(User).where(User.email == email))
    if not user:
        raise credentials_exception

    return user
