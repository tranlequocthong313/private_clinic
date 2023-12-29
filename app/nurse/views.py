from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_admin import expose
from sqlalchemy import func, or_, desc, case
from datetime import date

from . import nurse
from .forms import AppointmentDateForm
from ..main.forms import MedicalRegisterForm
from ..decorators import roles_required
from ..models import (
    AccountRole,
    User,
    MedicalRegistration,
    TimeToVisit,
    AppointmentSchedule,
    Policy,
)
from ..admin import ProtectedView, admin
from ..utils import random_password
from ..auth.views import register_handler
from ..sms import send_sms
from ..email import send_email
from .. import db
from ..main.views import register_medical


class NurseView(ProtectedView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_nurse()


class MedicalRegistrationView(NurseView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = MedicalRegisterForm()
        if form.validate_on_submit():
            register_medical(form)
            return redirect(url_for(".index"))
        return self.render("nurse/medical_register.html", form=form)


class AppointmentScheduleView(NurseView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = AppointmentDateForm()
        medical_registrations = MedicalRegistration.query
        appointment = AppointmentSchedule.query
        policy = Policy.query.get("so-benh-nhan")
        medical_registrations = medical_registrations.filter(
            func.date(MedicalRegistration.date_of_visit) <= form.date.data,
            MedicalRegistration.appointment_schedule_id == None,
        ).order_by(MedicalRegistration.date_of_visit)
        appointment = appointment.filter(AppointmentSchedule.date == form.date.data)
        all_fulfilled = True
        if appointment.first():
            for r in appointment.first().medical_registrations:
                if not r.fulfilled:
                    all_fulfilled = False
                    break
        return self.render(
            "nurse/appointment_schedule.html",
            medical_registrations=medical_registrations.all(),
            appointment=appointment.first(),
            policy=policy,
            date=form.date.data,
            form=form,
            can_add=form.date.data >= date.today()
            and (
                not appointment.first()
                or (
                    policy
                    and len(appointment.first().medical_registrations) < policy.value
                )
            ),
            can_edit=form.date.data >= date.today(),
            can_create=form.date.data >= date.today() and not all_fulfilled,
        )


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
