from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class MedicalForm(FlaskForm):
    name = StringField("Họ tên", validators=[DataRequired()])
    phone = StringField("Số điện thoại", validators=[DataRequired()])
    diagnosis = StringField("Chuan doan", validators=[DataRequired()])
    symptom = StringField("Trieu chung", validators=[DataRequired()])
    submit = SubmitField("Submit")
