"""empty message

Revision ID: efabb2c3b0a6
Revises: bfcae88209fe
Create Date: 2024-01-07 20:24:03.265072

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'efabb2c3b0a6'
down_revision = 'bfcae88209fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('medical_registrations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('symptom', sa.UnicodeText(), nullable=True),
    sa.Column('date_of_visit', sa.Date(), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=True),
    sa.Column('status', sa.Enum('REGISTERED', 'STAGING', 'SCHEDULED', 'CANCELED', 'ARRIVED', 'IN_PROGRESS', 'UNPAID', 'COMPLETED', name='medicalregistrationstatus'), nullable=True),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('appointment_schedule_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['appointment_schedule_id'], ['appointment_schedules.id'], ),
    sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('medical_examinations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('diagnosis', sa.UnicodeText(), nullable=True),
    sa.Column('advice', sa.UnicodeText(), nullable=True),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('fulfilled', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['id'], ['medical_registrations.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bills',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Double(), nullable=False),
    sa.Column('fulfilled', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('cashier_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['cashier_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['id'], ['medical_examinations.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
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
    op.drop_table('medical_registrations')
    # ### end Alembic commands ###
