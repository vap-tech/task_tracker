"""employee add task_count

Revision ID: f83530cc9b8c
Revises: 9b42f3c2eb04
Create Date: 2023-12-05 19:57:04.501545

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f83530cc9b8c'
down_revision = '9b42f3c2eb04'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('employee', sa.Column('task_count', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('employee', 'task_count')
    # ### end Alembic commands ###
