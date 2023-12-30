"""empty message

Revision ID: fc967d0c9789
Revises: 
Create Date: 2023-12-30 11:15:06.730207

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'fc967d0c9789'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medical_registrations', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=mysql.ENUM('NOT_VERIFIED', 'VERIFIED', 'NOT_SCHEDULED', 'SCHEDULED', 'ARRIVED', 'IN_PROGRESS', 'COMPLETED', collation='utf8mb4_general_ci'),
               type_=sa.Enum('NOT_VERIFIED', 'VERIFIED', 'STAGING', 'SCHEDULED', 'ARRIVED', 'IN_PROGRESS', 'COMPLETED', name='medicalregistrationstatus'),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medical_registrations', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=sa.Enum('NOT_VERIFIED', 'VERIFIED', 'STAGING', 'SCHEDULED', 'ARRIVED', 'IN_PROGRESS', 'COMPLETED', name='medicalregistrationstatus'),
               type_=mysql.ENUM('NOT_VERIFIED', 'VERIFIED', 'NOT_SCHEDULED', 'SCHEDULED', 'ARRIVED', 'IN_PROGRESS', 'COMPLETED', collation='utf8mb4_general_ci'),
               existing_nullable=True)

    # ### end Alembic commands ###
