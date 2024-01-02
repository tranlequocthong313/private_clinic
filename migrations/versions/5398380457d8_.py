"""empty message

Revision ID: 5398380457d8
Revises: f49405f77407
Create Date: 2024-01-02 11:03:21.649109

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5398380457d8'
down_revision = 'f49405f77407'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('medical_examinations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('diagnosis', sa.UnicodeText(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('medical_registration_id', sa.Integer(), nullable=False),
    sa.Column('fulfilled', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['medical_registration_id'], ['medical_registrations.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bills',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('amount', sa.Double(), nullable=False),
    sa.Column('fulfilled', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('cashier_id', sa.Integer(), nullable=False),
    sa.Column('medical_examination_id', sa.Integer(), nullable=False),
    sa.Column('policy', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['cashier_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['medical_examination_id'], ['medical_examinations.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['policy'], ['policies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('medical_examination_details',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('medical_examination_id', sa.Integer(), nullable=False),
    sa.Column('medicine_id', sa.String(length=50), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('dosage', sa.UnicodeText(), nullable=False),
    sa.ForeignKeyConstraint(['medical_examination_id'], ['medical_examinations.id'], ),
    sa.ForeignKeyConstraint(['medicine_id'], ['medicines.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('medical_examination_details')
    op.drop_table('bills')
    op.drop_table('medical_examinations')
    # ### end Alembic commands ###
