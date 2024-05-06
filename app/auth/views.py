from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_

from .. import db
from ..email import send_email
from ..models import User
from ..sms import send_otp
from . import auth
from .forms import LoginForm, RegisterAccountForm, VerifyOTPForm


@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    # INFO: send mail or phone number to verify user's account
    if current_user.email:
        return redirect(url_for("auth.send_mail_confirmation"))
    else:
        return redirect(url_for("auth.send_otp_confirmation"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            or_(
                User.email == form.email_phone.data.lower(),
                User.phone_number == form.email_phone.data.lower(),
            ),
        ).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get("next")
            if next is None or not next.startswith("/"):
                next = url_for("main.index")
            return redirect(next)
        flash("Email hoặc mật khẩu không đúng.", category="danger")
    return render_template("auth/login.html", form=form)


def register_handler(user):
    if not user.email and not user.phone_number:
        raise Exception("Phải cung cấp email hoặc số điện thoại.")
    db.session.add(user)
    db.session.commit()
    return user


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegisterAccountForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            password=form.password.data,
            date_of_birth=form.date_of_birth.data,
            address=form.address.data,
            gender=form.gender.data,
            email=form.email.data or None,
            phone_number=form.phone_number.data or None,
        )
        try:
            user = register_handler(user)
        except Exception as e:
            print(e)
            flash(e, category="danger")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


#######################
#### VERIFY BY OTP ####
#######################
@login_required
def send_otp_confirmation():
    if current_user.phone_number:
        send_otp(to=current_user.phone_number)
        flash(
            "Một mã OTP vừa được gửi cho bạn. Xin vùi lòng kiểm tra điện thoại.",
            category="info",
        )
    return redirect(url_for(".verify_otp"))


@auth.route("/verify-otp", methods=["GET", "POST"])
@login_required
def verify_otp():
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if not current_user.phone_number:
        return redirect(url_for("auth.send_mail_confirmation"))
    form = VerifyOTPForm()
    if form.validate_on_submit():
        otp = "".join(str(form[f"number_{i}"].data) for i in range(1, 7))
        if current_user.verify_otp(otp):
            current_user.confirmed = True
            db.session.commit()
            flash("Xác thực tài khoản thành công.", category="success")
        else:
            flash("Mã OTP không hợp lệ.", category="danger")
        return redirect(url_for("auth.verify_otp"))
    return render_template("auth/otp.html", form=form)


#######################
### VERIFY BY EMAIL ###
#######################
@auth.route("/confirm")
@login_required
def send_mail_confirmation():
    if not current_user.email:
        return redirect(url_for("auth.send_otp_confirmation"))
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email,
        "Xác nhận email",
        "auth/email/confirm_email",
        user=current_user,
        token=token,
    )
    flash(
        "Một email xác thực tài khoản vừa được gửi cho bạn. Xin vui lòng kiểm tra hòm thư.",
        category="info",
    )
    return render_template("auth/unconfirmed.html")


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        db.session.commit()
        flash("Bạn đã xác thực tài khoản thành công.", category="success")
    else:
        flash("Link xác thực không hợp lệ hoặc đã quá hạn.", category="danger")
    return redirect(url_for("main.index"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
