from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    IntegerField,
    BooleanField,
    SubmitField,
    DateField,
    SelectField,
    EmailField,
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp
from re import search

from ..models import User, Gender


class VerifyOTPForm(FlaskForm):
    number_1 = IntegerField()
    number_2 = IntegerField()
    number_3 = IntegerField()
    number_4 = IntegerField()
    number_5 = IntegerField()
    number_6 = IntegerField()
    submit = SubmitField("Xác thực")


class LoginForm(FlaskForm):
    email_phone = StringField(
        "Email hoac so dien thoai",
        validators=[
            Regexp(
                r"^(?:\d{10}|\w+@\w+\.\w{2,3})$",
                message="Enter a valid email or phone number.",
            ),
        ],
        render_kw={"placeholder": "Email hoac so dien thoai"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={"placeholder": "Mật khẩu"},
    )
    remember_me = BooleanField("Duy trì đăng nhập")
    submit = SubmitField("Đăng nhập")


class RegistrationForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired()],
        render_kw={"placeholder": "Họ tên"},
    )
    email = EmailField(
        "Email",
        render_kw={"placeholder": "Email"},
    )
    phone_number = StringField(
        "Phone number",
        render_kw={"placeholder": "Số điện thoại"},
    )
    address = StringField(
        "Address",
        validators=[DataRequired()],
        render_kw={"placeholder": "Địa chỉ"},
    )
    gender = SelectField(
        "Gender",
        choices=[(choice.name, choice.value) for choice in Gender],
        render_kw={"placeholder": "Giới tính"},
    )
    date_of_birth = DateField(
        "Date_of_birth",
        validators=[DataRequired()],
        format="%Y-%m-%d",
        render_kw={"placeholder": "Ngày sinh"},
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, max=32),
        ],
        render_kw={"placeholder": "Mật khẩu"},
    )
    password2 = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            Length(min=8, max=32),
            EqualTo("password", message="Passwords must match."),
        ],
        render_kw={"placeholder": "Nhập lại mật khẩu"},
    )

    submit = SubmitField("Đăng ký")

    def validate_email(self, field):
        if field.data and User.query.filter_by(email=field.data.lower()).first():
            field.errors.append("Email đã được đăng ký.")

    def validate_phone_number(self, field):
        if field.data and User.query.filter_by(phone_number=field.data.lower()).first():
            field.errors.append("Số điện thoại đã được đăng ký.")

    def validate(self, extra_validators=None):
        if super().validate(extra_validators):
            if not (self.email.data or self.phone_number.data):
                self.email.errors.append("Enter email or phone number.")
                self.phone_number.errors.append("Enter email or phone number.")
                return False
            else:
                email_matches = search(
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b",
                    self.email.data.lower(),
                )
                phone_matches = search(
                    r"(84|0[3|5|7|8|9])+([0-9]{8})\b", self.phone_number.data.lower()
                )
                if not (email_matches or phone_matches):
                    self.email.errors.append("Enter email or phone number.")
                    self.phone_number.errors.append("Enter email or phone number.")
                return True

        return False
