from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
    EmailField,
    DateField,
)
from wtforms.validators import DataRequired, Email
from re import search

from ..models import Gender, TimeToVisit, User


class MedicalRegisterForm(FlaskForm):
    name = StringField("Ho va ten", validators=[DataRequired()])
    gender = SelectField("Gioi tinh", choices=[g.value for g in (Gender)])
    date_of_birth = DateField("Ngay sinh")
    phone_number = StringField("So dien thoai")
    email = EmailField("Email")
    address = StringField("Dia chi")
    date_of_visit = DateField("Ngay hen", validators=[DataRequired()])
    time_to_visit = SelectField("Buoi hen", choices=[g.value for g in (TimeToVisit)])
    symptom = StringField("Trieu chung")
    callable_time = StringField("Thoi gian co the goi")
    submit = SubmitField("Dang ky")

    def validate_appointment_date(self, field):
        past = datetime.strptime(field.data, "%d/%m/%Y")
        present = datetime.now()
        if past.date() <= present.date():
            raise ValueError("Invalid appointment time.")

    def validate_email(self, field):
        if field.data and User.query.filter_by(email=field.data.lower()).first():
            raise ValueError("Email đã được đăng ký.")

    def validate_phone_number(self, field):
        if field.data and User.query.filter_by(phone_number=field.data.lower()).first():
            raise ValueError("Số điện thoại đã được đăng ký.")

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
                return True

        return False
