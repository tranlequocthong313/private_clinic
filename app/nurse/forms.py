from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class MedicalForm(FlaskForm):
    chuan_doan = PasswordField("Chuan doan", validators=[DataRequired()])
    dieu_tri = PasswordField("Dieu tri", validators=[DataRequired()])
    submit = SubmitField("Lap phieu kham")
