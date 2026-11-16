from datetime import datetime
from enum import StrEnum

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

# O registry guarda os metadados de todas as tabelas; o Alembic e os
# testes usam table_registry.metadata para saber o que criar.
table_registry = registry()


class TodoState(StrEnum):
    draft = "draft"
    todo = "todo"
    doing = "doing"
    done = "done"
    trash = "trash"


# mapped_as_dataclass transforma o model numa dataclass: User(...) recebe
# os campos como argumentos. init=False tira o campo do construtor (o
# banco é quem preenche id, created_at...).
@table_registry.mapped_as_dataclass
class User:
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, onupdate=func.now(), nullable=True
    )
    todos: Mapped[list["Todo"]] = relationship(
        init=False,
        back_populates="user",
        cascade="all, delete-orphan",
        # Em async não há lazy loading implícito: os todos são carregados
        # junto com o User (numa segunda query, SELECT ... WHERE IN).
        lazy="selectin",
    )


@table_registry.mapped_as_dataclass
class Todo:
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    state: Mapped[TodoState]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, onupdate=func.now(), nullable=True
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped[User] = relationship(init=False, back_populates="todos")
