"""empty message

Revision ID: 6d5a45a18d25
Revises: 5f09dc97b033
Create Date: 2023-11-25 10:22:44.978860

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6d5a45a18d25'
down_revision = '5f09dc97b033'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('date_of_birth',
               existing_type=sa.DATE(),
               nullable=True)
        batch_op.alter_column('address',
               existing_type=mysql.VARCHAR(collation='utf8mb4_general_ci', length=50),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('address',
               existing_type=mysql.VARCHAR(collation='utf8mb4_general_ci', length=50),
               nullable=False)
        batch_op.alter_column('date_of_birth',
               existing_type=sa.DATE(),
               nullable=False)

    # ### end Alembic commands ###
