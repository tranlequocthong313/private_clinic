from flask import render_template, session, flash, redirect, url_for
from flask_login import login_required, current_user

from . import main
from .forms import MedicalRegisterForm
from ..decorators import confirmed_required, roles_required
from ..dashboard_categories import dashboard_categories
from ..models import AccountRole, MedicalRegistration


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
        registration = MedicalRegistration(symptom=form.symptom.data)
        # id = Column(Integer, primary_key=True, autoincrement=True)
        # created_at = Column(DateTime, server_default=func.now())
        # symptom = Column(UnicodeText)
        # date_of_visit = Column(Date, nullable=False)
        # time_to_visit = Column(Enum(TimeToVisit), default=TimeToVisit.UNKNOWN)
        # fulfilled = Column(Boolean, default=False)
        # patient_id = Column(Integer, ForeignKey(User.id), nullable=False)
        # appointment_schedule_id = Column(
        #     Integer, ForeignKey(AppointmentSchedule.id), nullable=True
        # )

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
