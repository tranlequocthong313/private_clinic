from datetime import datetime, date
from time import time
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
    EmailField,
    DateField,
    TimeField,
)
from wtforms.validators import DataRequired, Email
from re import search

from ..models import Gender, User, AccountRole


class MedicalRegisterForm(FlaskForm):
    name = StringField("Ho va ten", validators=[DataRequired()])
    gender = SelectField(
        "Gioi tinh",
        choices=[g.value for g in (Gender)],
    )
    date_of_birth = DateField(
        "Ngay sinh",
    )
    phone_number = StringField("So dien thoai")
    email = EmailField("Email")
    address = StringField("Dia chi")
    date_of_visit = DateField("Ngay hen", validators=[DataRequired()])
    start_time = TimeField(
        "Gio tiep nhan (Sáng: 6h - 11h30, Chiều: 13h - 20h):",
        validators=[DataRequired()],
    )
    doctor = SelectField("Bac si kham")
    symptom = StringField("Trieu chung")
    callable_time = StringField("Thoi gian co the goi")
    submit = SubmitField("Dang ky")

    def __init__(self):
        super(MedicalRegisterForm, self).__init__()
        doctors = User.query.filter(User.role == AccountRole.DOCTOR).all()
        if not current_user.is_nurse:
            self.name.data = current_user.name
            self.gender.data = current_user.gender.value
            self.phone_number.data = current_user.phone_number
            self.email.data = current_user.email
            self.date_of_birth.data = current_user.date_of_birth
            self.address.data = current_user.address
       #self.date_of_visit.data = date.today()
        self.doctor.choices = [(d.id, d.name) for d in doctors]

    def validate_date_of_visit(self, field):
        if field.data < date.today():
            field.errors.append("Ngày hẹn không hợp lệ")

    def validate(self, extra_validators=None):
        if super().validate(extra_validators):
            if not (self.email.data or self.phone_number.data):
                self.email.errors.append("Enter email or phone number.")
                self.phone_number.errors.append("Enter email or phone number.")
                return False
            else:
                email_matches = search(
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b",
                    self.email.data.lower(),
                )
                phone_matches = search(
                    r"(84|0[3|5|7|8|9])+([0-9]{8})\b", self.phone_number.data.lower()
                )
                if not (email_matches or phone_matches):
                    self.email.errors.append("Enter email or phone number.")
                    self.phone_number.errors.append("Enter email or phone number.")
                    return False

            morning_start = (datetime.strptime("06:00:00", "%H:%M:%S")).time()
            morning_end = (datetime.strptime("11:30:00", "%H:%M:%S")).time()
            afternoon_start = (datetime.strptime("13:00:00", "%H:%M:%S")).time()
            afternoon_end = (datetime.strptime("20:00:00", "%H:%M:%S")).time()
            if not (
                morning_start <= self.start_time.data <= morning_end
                or afternoon_start <= self.start_time.data <= afternoon_end
            ):
                self.start_time.errors.append(
                    "Thời gian không hợp lệ. Hãy chọn thời gian trong khoảng 6h-11h30 hoặc 13h-20h."
                )
                return False
            if (
                self.date_of_visit.data == date.today()
                and self.start_time.data < datetime.now().time()
            ):
                self.start_time.errors.append("Hãy đăng ký giờ này vào ngày khác.")
                print(self.date_of_visit.data == date.today(),self.date_of_visit.data,date.today())
                return False
            return True

        return False


class SearchingMedicalRegistrationForm(FlaskForm):
    search = StringField("Tim kiem benh nhan")
    submit = SubmitField("Tim kiem")
