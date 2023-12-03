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

from ..models import Gender, TimeToVisit


class MedicalRegisterForm(FlaskForm):
    name = StringField("Ho va ten", validators=[DataRequired()])
    gender = SelectField("Gioi tinh", choices=[g.value for g in (Gender)])
    date_of_birth = DateField("Ngay sinh")
    phone_number = StringField("So dien thoai", validators=[DataRequired()])
    email = EmailField("Email")
    address = StringField("Dia chi")
    appointment_date = DateField("Ngay hen", validators=[DataRequired()])
    time_to_visit = SelectField("Buoi hen", choices=[g.value for g in (TimeToVisit)])
    symptom = StringField("Trieu chung")
    callable_time = StringField("Thoi gian co the goi")
    submit = SubmitField("Dang ky")

    def validate_appointment_date(self, field):
        past = datetime.strptime(field.data, "%d/%m/%Y")
        present = datetime.now()
        if past.date() <= present.date():
            raise ValueError("Invalid appointment time.")
