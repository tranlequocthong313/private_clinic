"""empty message

Revision ID: 6b3741bbb87d
Revises: 0539b7753acc
Create Date: 2024-01-02 11:58:16.268757

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6b3741bbb87d'
down_revision = '0539b7753acc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medical_registrations', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=mysql.ENUM('NOT_VERIFIED', 'VERIFIED', 'STAGING', 'SCHEDULED', 'CANCELED', 'ARRIVED', 'IN_PROGRESS', 'COMPLETED', collation='utf8mb4_general_ci'),
               type_=sa.Enum('NOT_VERIFIED', 'VERIFIED', 'STAGING', 'SCHEDULED', 'CANCELED', 'ARRIVED', 'IN_PROGRESS', 'UNPAID', 'COMPLETED', name='medicalregistrationstatus'),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medical_registrations', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=sa.Enum('NOT_VERIFIED', 'VERIFIED', 'STAGING', 'SCHEDULED', 'CANCELED', 'ARRIVED', 'IN_PROGRESS', 'UNPAID', 'COMPLETED', name='medicalregistrationstatus'),
               type_=mysql.ENUM('NOT_VERIFIED', 'VERIFIED', 'STAGING', 'SCHEDULED', 'CANCELED', 'ARRIVED', 'IN_PROGRESS', 'COMPLETED', collation='utf8mb4_general_ci'),
               existing_nullable=True)

    # ### end Alembic commands ###
