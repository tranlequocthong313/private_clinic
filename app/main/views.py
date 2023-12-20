from flask import render_template, session, flash, redirect, url_for
from flask_login import login_required, current_user

from . import main
from .forms import MedicalRegisterForm
from ..decorators import confirmed_required, roles_required
from ..dashboard_categories import dashboard_categories
from ..models import AccountRole, MedicalRegistration, User
from .. import db
from ..auth.views import register_handler


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
        patient_id = None
        if current_user.role == AccountRole.PATIENT:
            patient_id = current_user.id
        else:
            # create an account
            user = User(
                name=form.name.data,
                password=form.password.data,
                date_of_birth=form.date_of_birth.data,
                gender=form.gender.data,
            )
            try:
                user = register_handler(
                    user,
                    form.phone_number.data
                    if form.phone_number.data
                    else form.email.data,
                )
                patient_id = user.id
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


@main.route("/dashboard")
@login_required
@confirmed_required
@roles_required(
    [AccountRole.ADMIN, AccountRole.CASHIER, AccountRole.DOCTOR, AccountRole.NURSE]
)
def dashboard():
    return render_template("dashboard.html")


@main.app_context_processor
def inject_category():
    return dict(category=dashboard_categories.get(current_user.role.value, []))
