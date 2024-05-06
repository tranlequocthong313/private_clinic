from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    SubmitField,
)
from wtforms.validators import DataRequired


class AppointmentDateForm(FlaskForm):
    date = DateField("Ngày khám", validators=[DataRequired()], default=date.today())
    submit = SubmitField("Đồng ý")
