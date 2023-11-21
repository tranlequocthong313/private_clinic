"""empty message

Revision ID: 675b6a172b1d
Revises: 
Create Date: 2023-11-22 00:29:53.237527

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '675b6a172b1d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('medicine_types',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('medicine_units',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('policies',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('phone_number', sa.String(length=11), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('gender', sa.Enum('MALE', 'FEMALE', 'UNKNOWN', name='gender'), nullable=True),
    sa.Column('date_of_birth', sa.Date(), nullable=False),
    sa.Column('address', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('PATIENT', 'ADMIN', 'DOCTOR', 'NURSE', 'CASHIER', 'UNKNOWN', name='accountrole'), nullable=True),
    sa.Column('avatar', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_table('appointment_schedules',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('nurse_id', sa.Integer(), nullable=False),
    sa.Column('examination_date', sa.DateTime(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=False),
    sa.Column('policy', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['nurse_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['policy'], ['policies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('medical_examinations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('symptom', sa.String(length=100), nullable=False),
    sa.Column('diagnosis', sa.String(length=100), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('medicines',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('manufacturing_date', sa.Date(), nullable=False),
    sa.Column('expiry_date', sa.Date(), nullable=False),
    sa.Column('price', sa.Double(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('medicine_unit_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['medicine_unit_id'], ['medicine_units.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('bills',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('amount', sa.Double(), nullable=False),
    sa.Column('fulfilled', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('cashier_id', sa.Integer(), nullable=False),
    sa.Column('medical_examination_id', sa.Integer(), nullable=False),
    sa.Column('policy', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['cashier_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['medical_examination_id'], ['medical_examinations.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['policy'], ['policies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('medical_examination_detail',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('medical_examination_id', sa.Integer(), nullable=True),
    sa.Column('medicine_id', sa.String(length=50), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('dosage', sa.String(length=200), nullable=False),
    sa.ForeignKeyConstraint(['medical_examination_id'], ['medical_examinations.id'], ),
    sa.ForeignKeyConstraint(['medicine_id'], ['medicines.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('medical_registrations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('symptom', sa.String(length=100), nullable=True),
    sa.Column('date_of_visit', sa.Date(), nullable=False),
    sa.Column('time_to_visit', sa.Enum('MORNING', 'AFTERNOON', 'UNKNOWN', name='timetovisit'), nullable=True),
    sa.Column('fulfilled', sa.Boolean(), nullable=True),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('appointment_schedule_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['appointment_schedule_id'], ['appointment_schedules.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('medicine_medicine_type',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('medicine_type', sa.Integer(), nullable=True),
    sa.Column('medicine_id', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['medicine_id'], ['medicines.id'], ),
    sa.ForeignKeyConstraint(['medicine_type'], ['medicine_types.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('medicine_medicine_type')
    op.drop_table('medical_registrations')
    op.drop_table('medical_examination_detail')
    op.drop_table('bills')
    op.drop_table('medicines')
    op.drop_table('medical_examinations')
    op.drop_table('appointment_schedules')
    op.drop_table('users')
    op.drop_table('policies')
    op.drop_table('medicine_units')
    op.drop_table('medicine_types')
    # ### end Alembic commands ###