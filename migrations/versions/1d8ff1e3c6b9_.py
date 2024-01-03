"""empty message

Revision ID: 1d8ff1e3c6b9
Revises: 89afdcd62f08
Create Date: 2024-01-03 23:41:32.939482

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1d8ff1e3c6b9'
down_revision = '89afdcd62f08'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medical_registrations', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=mysql.ENUM('NOT_VERIFIED', 'VERIFIED', 'STAGING', 'SCHEDULED', 'CANCELED', 'ARRIVED', 'IN_PROGRESS', 'UNPAID', 'COMPLETED', collation='utf8mb4_general_ci'),
               type_=sa.Enum('REGISTERED', 'STAGING', 'SCHEDULED', 'CANCELED', 'ARRIVED', 'IN_PROGRESS', 'UNPAID', 'COMPLETED', name='medicalregistrationstatus'),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medical_registrations', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=sa.Enum('REGISTERED', 'STAGING', 'SCHEDULED', 'CANCELED', 'ARRIVED', 'IN_PROGRESS', 'UNPAID', 'COMPLETED', name='medicalregistrationstatus'),
               type_=mysql.ENUM('NOT_VERIFIED', 'VERIFIED', 'STAGING', 'SCHEDULED', 'CANCELED', 'ARRIVED', 'IN_PROGRESS', 'UNPAID', 'COMPLETED', collation='utf8mb4_general_ci'),
               existing_nullable=True)

    # ### end Alembic commands ###
