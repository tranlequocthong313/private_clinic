from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class MedicalForm(FlaskForm):
    chuan_doan = StringField("Chuan doan")
    dieu_tri = StringField("Dieu tri")
    submit = SubmitField("Lap phieu kham")
