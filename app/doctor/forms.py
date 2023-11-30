from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class MedicalForm(FlaskForm):
    chuan_doan = StringField("Chuan doan")
    trieu_chung = StringField("Trieu chung")
    submit = SubmitField("Lap phieu kham")
