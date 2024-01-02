import enum
import hashlib

from flask import current_app, request
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Double,
    Enum,
    ForeignKey,
    Integer,
    String,
    Unicode,
    UnicodeText,
    Time,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer

from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Gender(enum.Enum):
    MALE = "Male"
    FEMALE = "Female"


class AccountRole(enum.Enum):
    PATIENT = "Patient"
    ADMIN = "Admin"
    DOCTOR = "Doctor"
    NURSE = "Nurse"
    CASHIER = "Cashier"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50), unique=True)
    phone_number = Column(String(11), unique=True)
    name = Column(String(50), nullable=False)
    gender = Column(Enum(Gender), default=Gender.MALE)
    date_of_birth = Column(Date)
    address = Column(String(50))
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(AccountRole), default=AccountRole.PATIENT)
    confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    appointment_schedule = relationship(
        "AppointmentSchedule",
        backref="nurse",
        lazy=True,
        foreign_keys="AppointmentSchedule.nurse_id",
    )
    created_medical_examinations = relationship(
        "MedicalExamination",
        backref="doctor",
        lazy=True,
        foreign_keys="MedicalExamination.doctor_id",
    )
    own_medical_examinations = relationship(
        "MedicalExamination",
        backref="patient",
        lazy=True,
        foreign_keys="MedicalExamination.patient_id",
    )
    created_bills = relationship(
        "Bill", backref="cashier", lazy=True, foreign_keys="Bill.cashier_id"
    )
    own_bills = relationship(
        "Bill", backref="patient", lazy=True, foreign_keys="Bill.patient_id"
    )
    medical_registrations = relationship(
        "MedicalRegistration",
        backref="patient",
        lazy=True,
        foreign_keys="MedicalRegistration.patient_id",
    )
    medical = relationship(
        "MedicalRegistration",
        backref="doctor",
        lazy=True,
        foreign_keys="MedicalRegistration.doctor_id",
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<User {self.name}>"

    @property
    def is_admin(self):
        return self.role == AccountRole.ADMIN

    @property
    def is_patient(self):
        return self.role == AccountRole.PATIENT

    @property
    def is_doctor(self):
        return self.role == AccountRole.DOCTOR

    @property
    def is_nurse(self):
        return self.role == AccountRole.NURSE

    @property
    def is_cashier(self):
        return self.role == AccountRole.CASHIER

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @property
    def contact(self):
        return self.phone_number if self.phone_number else self.email

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        s = Serializer(current_app.config["SECRET_KEY"])
        return s.dumps(str(self.id), salt=current_app.config["SALT"])

    def confirm(self, token, exp=3600):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token, salt=current_app.config["SALT"], max_age=exp)
        except:
            return False
        if int(data) != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def gravatar(self, size=100, default="identicon", rating="g"):
        if request.is_secure:
            url = "https://secure.gravatar.com/avatar"
        else:
            url = "http://www.gravatar.com/avatar"
            hash = (
                hashlib.md5(self.email.encode("utf-8")).hexdigest()
                if self.email
                else ""
            )
        return "{url}/{hash}?s={size}&d={default}&r={rating}".format(
            url=url, hash=hash, size=size, default=default, rating=rating
        )


class AnonymousUser(AnonymousUserMixin):
    role = AccountRole.PATIENT


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Policy(db.Model):
    __tablename__ = "policies"

    id = Column(String(50), primary_key=True)
    name = Column(UnicodeText, nullable=False)
    value = Column(Integer, nullable=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Policy {self.name}>"


class AppointmentSchedule(db.Model):
    __tablename__ = "appointment_schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now())
    date = Column(Date, nullable=False, unique=True)
    nurse_id = Column(Integer, ForeignKey(User.id), nullable=False)
    medical_registrations = relationship(
        "MedicalRegistration", backref="appoitment_schedule", lazy=True
    )

    def __str__(self):
        return str(self.id)


class MedicalExaminationDetail(db.Model):
    __tablename__ = "medical_examination_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    medical_examination_id = Column(
        Integer, ForeignKey("medical_examinations.id"), nullable=False
    )
    medicine_id = Column(String(50), ForeignKey("medicines.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    dosage = Column(UnicodeText, nullable=False)

    def __str__(self):
        return str(self.id)


class MedicalExamination(db.Model):
    __tablename__ = "medical_examinations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now())
    diagnosis = Column(UnicodeText)
    patient_id = Column(Integer, ForeignKey(User.id), nullable=False)
    doctor_id = Column(Integer, ForeignKey(User.id), nullable=False)
    medical_registration_id = Column(
        Integer, ForeignKey("medical_registrations.id"), nullable=False
    )
    fulfilled = Column(Boolean, default=False)  # True = Fulfilled, False = Draft
    medical_examination_details = relationship(
        "MedicalExaminationDetail",
        backref="medical_examination",
        lazy=True,
    )

    def __str__(self):
        return str(self.id)


class Bill(db.Model):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Double, nullable=False)
    fulfilled = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    patient_id = Column(Integer, ForeignKey(User.id), nullable=False)
    cashier_id = Column(Integer, ForeignKey(User.id), nullable=False)
    medical_examination_id = Column(
        Integer, ForeignKey(MedicalExamination.id), nullable=False
    )
    policy = Column(String(50), ForeignKey(Policy.id), nullable=False)

    def __str__(self):
        return str(self.id)


class MedicalRegistrationStatus(enum.Enum):
    NOT_VERIFIED = "Not verified"
    VERIFIED = "Verified"
    STAGING = "staging"
    SCHEDULED = "Scheduled"
    CANCELED = "Canceled"
    ARRIVED = "Arrived"
    IN_PROGRESS = "In progress"
    UNPAID = "Unpaid"
    COMPLETED = "Completed"


class MedicalRegistration(db.Model):
    __tablename__ = "medical_registrations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now())
    symptom = Column(UnicodeText)
    date_of_visit = Column(Date, nullable=False)
    start_time = Column(Time)
    status = Column(
        Enum(MedicalRegistrationStatus), default=MedicalRegistrationStatus.NOT_VERIFIED
    )
    patient_id = Column(Integer, ForeignKey(User.id), nullable=False)
    doctor_id = Column(Integer, ForeignKey(User.id), nullable=False)
    appointment_schedule_id = Column(
        Integer, ForeignKey(AppointmentSchedule.id), nullable=True
    )
    medical_examination = relationship(
        "MedicalExamination", backref="medical_registration", lazy=True
    )

    def not_verified(self):
        return self.status == MedicalRegistrationStatus.NOT_VERIFIED

    def verified(self):
        return self.status == MedicalRegistrationStatus.VERIFIED

    def staging(self):
        return self.status == MedicalRegistrationStatus.STAGING

    def scheduled(self):
        return self.status == MedicalRegistrationStatus.SCHEDULED

    def arrived(self):
        return self.status == MedicalRegistrationStatus.ARRIVED

    def in_progress(self):
        return self.status == MedicalRegistrationStatus.IN_PROGRESS

    def completed(self):
        return self.status == MedicalRegistrationStatus.COMPLETED

    def __str__(self):
        return str(self.id)


class MedicineUnit(db.Model):
    __tablename__ = "medicine_units"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(50), nullable=False, unique=True)
    medicines = relationship("Medicine", backref="medicine_unit", lazy=True)

    def __str__(self):
        return self.name


class MedicineType(db.Model):
    __tablename__ = "medicine_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(50), nullable=False, unique=True)
    medicines = relationship(
        "Medicine_MedicineType", backref="medicine_type", lazy=True
    )

    def __str__(self):
        return self.name


class Medicine(db.Model):
    __tablename__ = "medicines"

    id = Column(String(50), primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    quantity = Column(Integer, nullable=False)
    manufacturing_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    price = Column(Double, nullable=False)
    description = Column(UnicodeText)
    medicine_unit_id = Column(Integer, ForeignKey(MedicineUnit.id), nullable=False)
    medicine_types = relationship(
        "Medicine_MedicineType", backref="medicine", lazy=True
    )
    medical_examination_details = relationship(
        "MedicalExaminationDetail",
        backref="medicine",
        lazy=True,
    )

    def __str__(self):
        return self.name

    @property
    def types(self):
        return ", ".join(
            [medicine_type.medicine_type.name for medicine_type in self.medicine_types]
        )


class Medicine_MedicineType(db.Model):
    __tablename__ = "medicine_medicinetype"

    id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_id = Column(String(50), ForeignKey(Medicine.id), nullable=False)
    medicine_type_id = Column(Integer, ForeignKey(MedicineType.id), nullable=False)

    def __str__(self):
        return self.medicine_type.name
