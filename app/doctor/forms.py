from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class MedicalForm(FlaskForm):
    diagnosis = StringField("Chuan doan")
    symptom = StringField("Trieu chung")
    submit = SubmitField("Lap phieu kham")
