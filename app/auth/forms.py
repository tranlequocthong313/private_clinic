import cloudinary.uploader
from dominate.tags import select, canvas
from flask import request

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from ..models import User, Gender


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Đăng nhập")


class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    phone_number = StringField("Phone_number", validators=[DataRequired(), Length(min=0, max=10)])
    address = StringField("Address", validators=[DataRequired()])
    gender = SelectField("Gender", choices=[(choice.name, choice.value) for choice in Gender])
    date_of_birth = DateField("Date_of_birth", validators=[DataRequired()], format='%Y-%m-%d')

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match."),
        ],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])

    submit = SubmitField("Đăng ký")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValueError("Email đã được đăng ký.")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValueError("Người dùng đã sẵn sàng sử dụng .")


