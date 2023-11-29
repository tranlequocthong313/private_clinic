from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

from ..models import User


class LoginForm(FlaskForm):
    email_phone = StringField(
        "Email hoac so dien thoai",
        validators=[
            Length(min=6, max=50),
            Regexp(
                r"^[0-9+\-.]+@[a-z\d\-.]+\.[a-z]+$",
                message="Enter a valid email or phone number.",
            ),
        ],
        render_kw={"placeholder": "Email hoac so dien thoai"},
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Đăng nhập")


class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email_phone = StringField(
        "Email hoac so dien thoai",
        validators=[
            Length(min=6, max=50),
            Regexp(
                r"^[0-9+\-.]+@[a-z\d\-.]+\.[a-z]+$",
                message="Enter a valid email or phone number.",
            ),
        ],
        render_kw={"placeholder": "Email hoac so dien thoai"},
    )
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
            raise ValueError("Email already registered.")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValueError("Username already in use.")
