"""comments

Revision ID: 638b5cfed907
Revises: d6a08a1eb0c1
Create Date: 2025-04-17 22:38:00.434247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '638b5cfed907'
down_revision: Union[str, None] = 'd6a08a1eb0c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('comment', sa.TEXT(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'comment')
    # ### end Alembic commands ###
