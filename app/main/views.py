from flask import render_template, session, flash, redirect, url_for
from flask_login import login_required, current_user

from . import main
from .forms import MedicalRegisterForm
from ..decorators import confirmed_required, roles_required
from ..dashboard_categories import dashboard_categories
from ..models import AccountRole, MedicalRegistration, User
from .. import db
from ..auth.views import register_handler
from ..utils import random_password
from ..sms import send_sms
from ..email import send_email


@main.route("/")
def index():
    return render_template("landing_page.html")


@main.route("/contact")
def contact():
    return render_template("contact.html")


@main.route("/about")
def about():
    return render_template("about.html")


@main.route("/medical-register", methods=["GET", "POST"])
@login_required
@confirmed_required
@roles_required([AccountRole.PATIENT, AccountRole.NURSE])
def medical_register():
    form = MedicalRegisterForm()
    if form.validate_on_submit():
        patient_id = None
        if current_user.is_patient():
            patient_id = current_user.id
        else:
            password = random_password()
            user = User(
                name=form.name.data,
                password=password,
                date_of_birth=form.date_of_birth.data,
                gender=form.gender.data,
                email=form.email.data if form.email.data else None,
                phone_number=form.phone_number.data if form.phone_number.data else None,
            )
            try:
                user = register_handler(
                    user,
                )
                patient_id = user.id
                if user.email:
                    send_email(
                        user.email,
                        "Account",
                        "auth/email/account",
                        user=user,
                        password=password,
                    )
                if user.phone_number:
                    send_sms(
                        user.phone_number,
                        f"Account: Phone number: {user.phone_number}, Password: {password}",
                    )
            except Exception as e:
                flash(e)

        registration = MedicalRegistration(
            symptom=form.symptom.data,
            date_of_visit=form.date_of_visit.data,
            time_to_visit=form.time_to_visit.data,
            patient_id=patient_id,
        )
        db.session.add(registration)
        db.session.commit()

        flash("Dang ky thanh cong.")
        return redirect(url_for("main.medical_register"))
    return render_template("medical_register.html", form=form)


# @main.route("/dashboard")
# @login_required
# @confirmed_required
# @roles_required(
#     [AccountRole.ADMIN, AccountRole.CASHIER, AccountRole.DOCTOR, AccountRole.NURSE]
# )
# def dashboard():
#     return render_template("dashboard.html")


@main.app_context_processor
def inject_category():
    return dict(category=dashboard_categories.get(current_user.role.value, []))
