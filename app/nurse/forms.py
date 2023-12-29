from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired
from datetime import date


class AppointmentDateForm(FlaskForm):
    date = DateField("Ngay kham", validators=[DataRequired()], default=date.today())
    submit = SubmitField("Dong y")
