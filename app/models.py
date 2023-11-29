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
    MALE = "Nam"
    FEMALE = "Nữ"
    UNKNOWN = "Không xác định"


class AccountRole(enum.Enum):
    PATIENT = "Patient"
    ADMIN = "Admin"
    DOCTOR = "Doctor"
    NURSE = "Nurse"
    CASHIER = "Cashier"
    UNKNOWN = "Unknown"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50), nullable=False, unique=True)
    phone_number = Column(String(11), unique=True)
    name = Column(String(50), nullable=False)
    gender = Column(Enum(Gender), default=Gender.UNKNOWN)
    date_of_birth = Column(Date)
    address = Column(String(50))
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(AccountRole), default=AccountRole.UNKNOWN)
    avatar = Column(String(255))
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
        "MedicalRegistration", backref="patient", lazy=True
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<User {self.name}>"

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

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
            hash = hashlib.md5(self.email.encode("utf-8")).hexdigest()
        return "{url}/{hash}?s={size}&d={default}&r={rating}".format(
            url=url, hash=hash, size=size, default=default, rating=rating
        )


class AnonymousUser(AnonymousUserMixin):
    role = AccountRole.UNKNOWN


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Policy(db.Model):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
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
    nurse_id = Column(Integer, ForeignKey(User.id), nullable=False)
    examination_date = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    policy = Column(Integer, ForeignKey(Policy.id), nullable=False)

    def __str__(self):
        return self.id


medical_examination_detail = db.Table(
    "medical_examination_detail",
    db.Column("id", db.Integer, primary_key=True, autoincrement=True),
    db.Column(
        "medical_examination_id", db.Integer, db.ForeignKey("medical_examinations.id")
    ),
    db.Column("medicine_id", db.String(50), db.ForeignKey("medicines.id")),
    db.Column("quantity", db.Integer, nullable=False),
    db.Column("dosage", UnicodeText, nullable=False),
)


class MedicalExamination(db.Model):
    __tablename__ = "medical_examinations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now())
    symptom = Column(UnicodeText, nullable=False)
    diagnosis = Column(UnicodeText, nullable=False)
    patient_id = Column(Integer, ForeignKey(User.id), nullable=False)
    doctor_id = Column(Integer, ForeignKey(User.id), nullable=False)
    medicines = relationship(
        "Medicine",
        secondary=medical_examination_detail,
        backref="medicine_examination",
        lazy=True,
    )

    def __str__(self):
        return self.id


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
    policy = Column(Integer, ForeignKey(Policy.id), nullable=False)

    def __str__(self):
        return self.id


class TimeToVisit(enum.Enum):
    MORNING = "Morning"
    AFTERNOON = "Afternoon"
    UNKNOWN = "Unknown"


class MedicalRegistration(db.Model):
    __tablename__ = "medical_registrations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now())
    symptom = Column(UnicodeText)
    date_of_visit = Column(Date, nullable=False)
    time_to_visit = Column(Enum(TimeToVisit), default=TimeToVisit.UNKNOWN)
    fulfilled = Column(Boolean, default=False)
    patient_id = Column(Integer, ForeignKey(User.id), nullable=False)
    appointment_schedule_id = Column(
        Integer, ForeignKey(AppointmentSchedule.id), nullable=True
    )

    def __str__(self):
        return self.id


medicine_type = db.Table(
    "medicine_medicine_type",
    db.Column("id", db.Integer, primary_key=True, autoincrement=True),
    db.Column("medicine_type", db.Integer, db.ForeignKey("medicine_types.id")),
    db.Column("medicine_id", db.String(50), db.ForeignKey("medicines.id")),
)


class MedicineUnit(db.Model):
    __tablename__ = "medicine_units"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(50), nullable=False, unique=True)
    medicines = relationship("Medicine", backref="medicine_unit", lazy=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<MedicineUnit {self.name}>"


class MedicineType(db.Model):
    __tablename__ = "medicine_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(50), nullable=False, unique=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<MedicineType {self.name}>"


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

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Medicine {self.name}>"
