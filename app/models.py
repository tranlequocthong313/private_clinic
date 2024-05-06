import enum
import hashlib
from datetime import date

from flask import current_app, request
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
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
    Time,
    Unicode,
    UnicodeText,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager, sms_client


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
    indicated_medical_registers = relationship(
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
        return self.phone_number or self.email

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        s = Serializer(current_app.config["SECRET_KEY"])
        return s.dumps(str(self.id), salt=current_app.config["SALT"])

    def confirm(self, token, exp=3600):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token, salt=current_app.config["SALT"], max_age=exp)
        except Exception:
            return False
        if int(data) != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def verify_otp(self, otp_code):
        otp_verification_check = sms_client.verify.v2.services(
            current_app.config.get("TWILIO_SERVICE_SID")
        ).verification_checks.create(to=f"+84{self.phone_number}", code=otp_code)
        return otp_verification_check is not None

    def gravatar(self, size=100, default="identicon", rating="g"):
        hash = ""
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


class PolicyType(enum.Enum):
    EXAMINATION_FEE = "Examination Fee"
    NUMBER_OF_PATIENTS = "Number of Patients"


class Policy(db.Model):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(UnicodeText, nullable=False)
    value = Column(Integer, nullable=False)
    type = Column(Enum(PolicyType))

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
        "MedicalRegistration", backref="appointment_schedule", lazy=True
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

    id = Column(Integer, ForeignKey("medical_registrations.id"), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    diagnosis = Column(UnicodeText)
    advice = Column(UnicodeText)
    patient_id = Column(Integer, ForeignKey(User.id), nullable=False)
    doctor_id = Column(Integer, ForeignKey(User.id), nullable=False)
    fulfilled = Column(Boolean, default=False)
    medical_examination_details = relationship(
        "MedicalExaminationDetail",
        backref="medical_examination",
        lazy=True,
    )
    bill = relationship("Bill", backref="medical_examination", lazy=True, uselist=False)

    def __str__(self):
        return str(self.id)


class Bill(db.Model):
    __tablename__ = "bills"

    id = Column(Integer, ForeignKey(MedicalExamination.id), primary_key=True)
    amount = Column(Double, nullable=False)
    fulfilled = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    patient_id = Column(Integer, ForeignKey(User.id), nullable=False)
    cashier_id = Column(Integer, ForeignKey(User.id), nullable=False)

    def __str__(self):
        return str(self.id)


class MedicalRegistrationStatus(enum.Enum):
    REGISTERED = "Registered"  # Registered successfully
    STAGING = "Staging"  # Waiting for being scheduled
    SCHEDULED = "Scheduled"  # Being scheduled by nurses
    CANCELED = "Canceled"  # Canceled schedule
    ARRIVED = "Arrived"  # Waiting in the clinic
    IN_PROGRESS = "In progress"  # Being examined by doctors
    UNPAID = "Unpaid"  # Finished examining but unpaid
    COMPLETED = "Completed"  # Paid successfully


class MedicalRegistration(db.Model):
    __tablename__ = "medical_registrations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now())
    symptom = Column(UnicodeText)
    date_of_visit = Column(Date, nullable=False)
    start_time = Column(Time)
    status = Column(
        Enum(MedicalRegistrationStatus), default=MedicalRegistrationStatus.REGISTERED
    )
    patient_id = Column(Integer, ForeignKey(User.id), nullable=False)
    doctor_id = Column(Integer, ForeignKey(User.id), nullable=False)
    appointment_schedule_id = Column(
        Integer, ForeignKey(AppointmentSchedule.id), nullable=True
    )
    medical_examination = relationship(
        "MedicalExamination", backref="medical_registration", lazy=True, uselist=False
    )

    @property
    def registered(self):
        return self.status == MedicalRegistrationStatus.REGISTERED

    @property
    def staging(self):
        return self.status == MedicalRegistrationStatus.STAGING

    @property
    def canceled(self):
        return self.status == MedicalRegistrationStatus.CANCELED

    @property
    def scheduled(self):
        return self.status == MedicalRegistrationStatus.SCHEDULED

    @property
    def arrived(self):
        return self.status == MedicalRegistrationStatus.ARRIVED

    @property
    def in_progress(self):
        return self.status == MedicalRegistrationStatus.IN_PROGRESS

    @property
    def unpaid(self):
        return self.status == MedicalRegistrationStatus.UNPAID

    @property
    def completed(self):
        return self.status == MedicalRegistrationStatus.COMPLETED

    @property
    def can_be_removed_from_schedule(self):
        return self.registered or self.staging or self.canceled or self.scheduled

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


def create_default_data():
    if not db.session.query(User).count():
        _create_users()
    if not db.session.query(Policy).count():
        policy1 = Policy(
            name="Number of Patients Policy",
            value=40,
            type=PolicyType.NUMBER_OF_PATIENTS,
        )
        policy2 = Policy(
            name="Examination Fee Policy", value=100000, type=PolicyType.EXAMINATION_FEE
        )

        _create_bulk("CREATED POLICIES", policy1, policy2)
    if not db.session.query(MedicineUnit).count():
        medicine_unit1 = MedicineUnit(name="Vien")
        medicine_unit2 = MedicineUnit(name="Chai")

        _create_bulk( "CREATED MEDICINE UNITS", medicine_unit1, medicine_unit2)
    if not db.session.query(MedicineType).count():
        medicine_type1 = MedicineType(name="Cam cum")
        medicine_type2 = MedicineType(name="Khang sinh")

        _create_bulk( "CREATED MEDICINE TYPES", medicine_type1, medicine_type2)
    if not db.session.query(Medicine).count():
        medicine_units = MedicineUnit.query.all()

        medicine1 = Medicine(
            id="paracetamol",
            name="Paracetamol",
            quantity=100,
            manufacturing_date=date(2022, 1, 1),
            expiry_date=date(2023, 1, 1),
            price=10.0,
            description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum blandit ultrices velit. In nec mi accumsan, tristique urna at, vestibulum augue. Vivamus finibus ligula et elementum hendrerit. Quisque hendrerit lobortis condimentum. Donec in condimentum risus.",
            medicine_unit=medicine_units[0],
        )
        medicine2 = Medicine(
            id="panadol",
            name="Panadol",
            quantity=200,
            manufacturing_date=date(2021, 1, 1),
            expiry_date=date(2023, 1, 1),
            price=20.0,
            description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum blandit ultrices velit. In nec mi accumsan, tristique urna at, vestibulum augue. Vivamus finibus ligula et elementum hendrerit. Quisque hendrerit lobortis condimentum. Donec in condimentum risus.",
            medicine_unit=medicine_units[1],
        )

        _create_bulk("CREATED MEDICINES", medicine1, medicine2)
    if not db.session.query(Medicine_MedicineType).count():
        medicine_types = MedicineType.query.all()
        medicines = Medicine.query.all()
        m1 = Medicine_MedicineType(
            medicine_id=medicines[0].id, medicine_type_id=medicine_types[0].id
        )
        m2 = Medicine_MedicineType(
            medicine_id=medicines[1].id, medicine_type_id=medicine_types[1].id
        )
        _create_bulk("CREATED MEDICINE_MEDICINETYPES", m1, m2)
    print("Default data created successfully!")


# TODO Rename this here and in `create_default_data`
def _create_users():
    doctor1 = User(
        email="tranlethong@gmail.com",
        name="Doctor 1",
        role=AccountRole.DOCTOR,
        confirmed=True,
        password="password",
    )
    doctor2 = User(
        email="school0123456@gmail.com",
        name="Doctor 2",
        role=AccountRole.DOCTOR,
        confirmed=True,
        password="password",
    )

    nurse1 = User(
        email="hadep7a@gmail.com",
        name="Nurse 1",
        role=AccountRole.NURSE,
        confirmed=True,
        password="password",
    )
    nurse2 = User(
        email="2151050438thong@ou.edu.vn",
        name="Nurse 2",
        role=AccountRole.NURSE,
        confirmed=True,
        password="password",
    )

    cashier1 = User(
        email="2151053013ha@ou.edu.vn",
        name="Cashier 1",
        role=AccountRole.CASHIER,
        confirmed=True,
        password="password",
    )
    cashier2 = User(
        email="thong@gmail.com",
        name="Cashier 2",
        role=AccountRole.CASHIER,
        confirmed=True,
        password="password",
    )

    admin1 = User(
        email="tranlequocthong313@gmail.com",
        name="Admin 1",
        role=AccountRole.ADMIN,
        confirmed=True,
        password="password",
    )
    admin2 = User(
        email="admin2@example.com",
        name="Admin 2",
        role=AccountRole.ADMIN,
        confirmed=True,
        password="password",
    )

    patient1 = User(
        email="thongtranlequoc@gmail.com",
        name="Patient 1",
        role=AccountRole.PATIENT,
        confirmed=True,
        password="password",
    )
    patient2 = User(
        email="patient2@example.com",
        name="Patient 2",
        role=AccountRole.PATIENT,
        confirmed=True,
        password="password",
    )

    users = [
        doctor1,
        doctor2,
        nurse1,
        nurse2,
        cashier1,
        cashier2,
        admin1,
        admin2,
        patient1,
        patient2,
    ]
    db.session.add_all(users)
    db.session.commit()
    print("CREATED USERS")


def _create_bulk(msg, *args):
    db.session.add_all(args)
    db.session.commit()
    print(msg)
