from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField
from wtforms.validators import DataRequired, Email


class SearchingPatientForm(FlaskForm):
    id = IntegerField("Ma benh nhan")
    email = EmailField("Email")
    phone_number = StringField("So dien thoai")
    submit = SubmitField("Tra cuu")
