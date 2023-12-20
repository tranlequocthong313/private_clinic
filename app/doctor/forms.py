from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class MedicalForm(FlaskForm):
    name = StringField("Họ tên")
    phone = StringField("Số điện thoại")
    diagnosis = StringField("Chuan doan")
    symptom = StringField("Trieu chung")
    submit = SubmitField("Lưu")
