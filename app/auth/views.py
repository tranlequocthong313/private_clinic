from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from sqlalchemy import or_
from re import search
from . import auth
from ..models import User
from ..email import send_email
from ..sms import send_sms
from .forms import LoginForm, RegistrationForm

from .. import db


@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        print(form.email_phone.data)
        user = User.query.filter(
            or_(
                User.email == form.email_phone.data.lower(),
                User.phone_number == form.email_phone.data.lower(),
            ),
            User.password == form.password.data,
        ).first()
        print(
            or_(
                User.email == form.email_phone.data.lower(),
                User.phone_number == form.email_phone.data.lower(),
            )
        )
        print(user)
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get("next")
            if next is None or not next.startswith("/"):
                next = url_for("main.index")
            return redirect(next)
        flash("Invalid email or password.")
    return render_template("auth/login.html", form=form)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    print(form.password.data, form.email_phone.data)
    if form.validate_on_submit():
        print("VALID REGISTER")
        user = User(
            name=form.name.data,
            # email=form.email.data.lower(),
            # phone_number=form.email_phone.data.lower(),
            password=form.password.data,
            date_of_birth=form.date_of_birth.data,
            address=form.address.data,
            gender=form.gender.data,
        )

        matches = search(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b",
            form.email_phone.data.lower(),
        )
        print("mail", matches)
        if matches:
            user.email = form.email_phone.data.lower()
        matches = search(
            r"(84|0[3|5|7|8|9])+([0-9]{8})\b", form.email_phone.data.lower()
        )
        print("phone", matches)
        if matches:
            user.phone_number = form.email_phone.data.lower()
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        if user.email:
            send_email(
                user.email,
                "Confirm Your Account",
                "auth/email/confirm",
                user=user,
                token=token,
            )
        if user.phone_number:
            send_sms(user.phone_number, "Hi from server")
        flash("A confirmation email has been sent to you by email.")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        db.session.commit()
        flash("You have confirmed your account. Thanks!")
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for("main.index"))


@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email,
        "Confirm Your Account",
        "auth/email/confirm",
        user=current_user,
        token=token,
    )
    flash("A new confirmation email has been sent to you by email.")
    return redirect(url_for("main.index"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main.index"))
