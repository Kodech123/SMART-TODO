"""add reminder opened_at

Revision ID: 38a99224a02a
Revises: b0354546fbb7
Create Date: 2026-08-12 23:00:16.207372

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38a99224a02a'
down_revision: Union[str, None] = 'b0354546fbb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # apscheduler_jobs is created/managed by APScheduler's SQLAlchemyJobStore at
    # runtime, not by our models -- autogenerate flags it as "should be dropped"
    # since it isn't in our metadata; that diff is intentionally omitted here.
    op.add_column('reminders', sa.Column('opened_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('reminders', 'opened_at')
