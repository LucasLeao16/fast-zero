"""Dependências reutilizáveis das rotas.

`Annotated[Tipo, Depends(função)]` diz ao FastAPI: "para preencher este
parâmetro, chame a função". Os apelidos abaixo evitam repetir isso em
cada rota.
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.utils.security import get_current_user

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
T_CurrentUser = Annotated[User, Depends(get_current_user)]
