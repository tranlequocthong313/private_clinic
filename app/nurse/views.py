from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_admin import expose

from . import nurse
from .forms import MedicalForm
from ..main.forms import MedicalRegisterForm
from ..decorators import roles_required
from ..models import AccountRole, User, MedicalRegistration
from ..admin import ProtectedView, admin
from ..utils import random_password
from ..auth.views import register_handler
from ..sms import send_sms
from ..email import send_email
from .. import db


class NurseView(ProtectedView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_nurse()


class MedicalRegistrationView(NurseView):
    @expose("/")
    def index(self):
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
                    phone_number=form.phone_number.data
                    if form.phone_number.data
                    else None,
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
        return self.render("nurse/medical_register.html", form=form)


class AppointmentScheduleView(NurseView):
    @expose("/")
    def index(self):
        return self.render("nurse/appointment_schedule.html")


admin.add_view(
    AppointmentScheduleView(
        name="Lập danh sách khám bệnh",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="appointment-schedule",
    )
)
admin.add_view(
    MedicalRegistrationView(
        name="Đăng ký khám bệnh",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="medical-register",
    )
)
