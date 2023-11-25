from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class MedicalRegisterForm(FlaskForm):
    buoi_hen = StringField("Buoi hen", validators=[DataRequired()])
    trieu_chung = PasswordField("Trieu Chung", validators=[DataRequired()])
    sdt = PasswordField("SDT", validators=[DataRequired()])
    submit = SubmitField("Dang ky")
