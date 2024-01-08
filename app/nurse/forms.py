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
    date = DateField("Ngày khám", validators=[DataRequired()], default=date.today())
    submit = SubmitField("Đồng ý")
