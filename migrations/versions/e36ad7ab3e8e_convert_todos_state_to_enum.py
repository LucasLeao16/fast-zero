"""convert todos state to enum

A migração inicial criou todos.state como VARCHAR, mas o model declara
um Enum. Esta migração alinha o banco com o model.

Revision ID: e36ad7ab3e8e
Revises: 8c66d73321e6
Create Date: 2026-11-16 20:56:38.084534

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e36ad7ab3e8e'
down_revision: Union[str, None] = '8c66d73321e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

todostate = sa.Enum(
    'draft', 'todo', 'doing', 'done', 'trash', name='todostate'
)


def upgrade() -> None:
    # O alter_column não cria o tipo ENUM no Postgres; criamos antes.
    todostate.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        'todos',
        'state',
        existing_type=sa.VARCHAR(),
        type_=todostate,
        existing_nullable=False,
        # Converte os valores de texto já existentes para o novo tipo
        postgresql_using='state::todostate',
    )


def downgrade() -> None:
    op.alter_column(
        'todos',
        'state',
        existing_type=todostate,
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using='state::text',
    )
    todostate.drop(op.get_bind(), checkfirst=True)
