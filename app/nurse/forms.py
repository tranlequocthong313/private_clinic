from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    DateField,
    SelectField,
    HiddenField,
)
from wtforms.validators import DataRequired
from datetime import date
from ..models import MedicalRegistrationStatus


class AppointmentDateForm(FlaskForm):
    date = DateField("Ngay kham", validators=[DataRequired()], default=date.today())
    submit = SubmitField("Dong y")


class SearchingMedicalRegistrationForm(FlaskForm):
    search = StringField("Tim kiem benh nhan")
    submit = SubmitField("Tim kiem")
