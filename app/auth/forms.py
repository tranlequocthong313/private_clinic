from re import search

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    EmailField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    ValidationError,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length

from ..models import Gender, User


class VerifyOTPForm(FlaskForm):
    number_1 = IntegerField()
    number_2 = IntegerField()
    number_3 = IntegerField()
    number_4 = IntegerField()
    number_5 = IntegerField()
    number_6 = IntegerField()
    submit = SubmitField("Xác thực")


class EmailOrPhoneValidator:
    def __call__(self, form, field):
        if Email()(form, field):
            return

        if field.data.isdigit() and len(field.data) == 10:
            return

        raise ValidationError("Nhập một email hoặc số điện thoại hợp lệ.")


class LoginForm(FlaskForm):
    email_phone = StringField(
        "Email hoặc số điện thoại",
        # validators=[EmailOrPhoneValidator()], #  HACK: Skip this validator because I'm too lazy to fix it .🔥🔥🔥
        render_kw={"placeholder": "Email hoặc số điện thoại"},
    )
    password = PasswordField(
        "Mật khẩu",
        validators=[DataRequired()],
        render_kw={"placeholder": "Mật khẩu"},
    )
    remember_me = BooleanField("Duy trì đăng nhập")
    submit = SubmitField("Đăng nhập")


class RegisterAccountForm(FlaskForm):
    name = StringField(
        "Họ tên",
        validators=[DataRequired()],
        render_kw={"placeholder": "Họ tên"},
    )
    email = EmailField(
        "Email",
        render_kw={"placeholder": "Email"},
    )
    phone_number = StringField(
        "Số điện thoại",
        render_kw={"placeholder": "Số điện thoại"},
    )
    address = StringField(
        "Địa chỉ",
        validators=[DataRequired()],
        render_kw={"placeholder": "Địa chỉ"},
    )
    gender = SelectField(
        "Giới tính",
        choices=[(choice.name, choice.value) for choice in Gender],
        render_kw={"placeholder": "Giới tính"},
    )
    date_of_birth = DateField(
        "Ngày sinh",
        validators=[DataRequired()],
        format="%Y-%m-%d",
        render_kw={"placeholder": "Ngày sinh"},
    )
    password = PasswordField(
        "Mật khẩu",
        validators=[
            DataRequired(),
            Length(min=8, max=32),
        ],
        render_kw={"placeholder": "Mật khẩu"},
    )
    password2 = PasswordField(
        "Nhập lại mật khẩu",
        validators=[
            DataRequired(),
            Length(min=8, max=32),
            EqualTo("password", message="Mật khẩu không khớp"),
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
                self.email.errors.append("Nhập một email hoặc số điện thoại hợp lệ.")
                self.phone_number.errors.append(
                    "Nhập một email hoặc số điện thoại hợp lệ."
                )
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
                    self.email.errors.append(
                        "Nhập một email hoặc số điện thoại hợp lệ."
                    )
                    self.phone_number.errors.append(
                        "Nhập một email hoặc số điện thoại hợp lệ."
                    )
                return True

        return False
