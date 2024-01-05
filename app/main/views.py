from flask import render_template, session, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, or_, desc, case

from . import main
from .forms import MedicalRegisterForm
from ..decorators import confirmed_required, roles_required
from ..models import AccountRole, MedicalRegistration, User, MedicalRegistrationStatus
from .. import db
from ..auth.views import register_handler
from ..utils import random_password
from ..sms import send_sms
from ..email import send_email
from datetime import datetime, timedelta


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
def medical_register():
    form = MedicalRegisterForm()
    if form.validate_on_submit():
        success = register_medical(form)
        if success:
            return redirect(url_for("main.medical_register"))
    return render_template("medical_register.html", form=form)


def register_medical(form):
    patient_id = None
    if current_user.is_patient:
        patient_id = current_user.id
    else:
        user = User.query.filter(
            or_(
                User.phone_number == form.phone_number.data,
                User.email == form.email.data,
            )
        ).first()
        if not user:
            password = random_password()
            user = User(
                name=form.name.data,
                password=password,
                date_of_birth=form.date_of_birth.data,
                gender=form.gender.data,
                address=form.address.data,
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
                        "Tài khoản phòng khám",
                        "auth/email/account_email",
                        patient=user,
                        password=password,
                    )
                if user.phone_number:
                    send_sms(
                        user.phone_number,
                        "auth/sms/account_sms",
                        patient=user,
                        password=password,
                    )
            except Exception as e:
                flash(e, category="danger")
        else:
            patient_id = user.id

    registered = False
    for r in MedicalRegistration.query.filter(
        MedicalRegistration.date_of_visit == form.date_of_visit.data,
        MedicalRegistration.doctor_id == form.doctor.data,
    ).all():
        start_time = form.start_time.data
        end_time = (
            datetime.strptime(str(form.start_time.data), "%H:%M:%S")
            + timedelta(minutes=30)
        ).time()
        current_end_time = (
            datetime.strptime(str(r.start_time), "%H:%M:%S") + timedelta(minutes=30)
        ).time()
        if start_time < current_end_time and r.start_time < end_time:
            registered = True
            break

    if registered:
        flash("Đã có người đăng ký bác sĩ vào thời gian này.", category="danger")
        return False
    else:
        registration = MedicalRegistration(
            symptom=form.symptom.data,
            date_of_visit=form.date_of_visit.data,
            start_time=form.start_time.data,
            patient_id=patient_id,
            doctor_id=form.doctor.data,
        )
        db.session.add(registration)
        db.session.commit()
        flash("Đăng ký thành công.", category="success")
        return True
