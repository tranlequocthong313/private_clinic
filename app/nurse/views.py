from datetime import date

from flask import redirect, url_for
from flask_admin import expose
from flask_login import current_user
from sqlalchemy import func

from ..dashboard import DashboardView, dashboard
from ..main.forms import MedicalRegisterForm
from ..main.views import register_medical
from ..models import (
    AppointmentSchedule,
    MedicalRegistration,
    MedicalRegistrationStatus,
    Policy,
    PolicyType,
)
from ..patient.views import ListPatientView
from .forms import AppointmentDateForm


class NurseView(DashboardView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_nurse


class MedicalRegisterView(NurseView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = MedicalRegisterForm()
        if form.validate_on_submit():
            if _ := register_medical(form):
                return redirect(url_for(".index"))
        return self.render("medical_register.html", form=form)


class AppointmentScheduleView(NurseView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = AppointmentDateForm()
        medical_registrations = MedicalRegistration.query
        appointment = AppointmentSchedule.query
        policy = Policy.query.filter(Policy.type == PolicyType.NUMBER_OF_PATIENTS).first()
        medical_registrations = medical_registrations.filter(
            func.date(MedicalRegistration.date_of_visit) <= form.date.data,
            MedicalRegistration.status == MedicalRegistrationStatus.REGISTERED,
        ).order_by(MedicalRegistration.date_of_visit)
        appointment = appointment.filter(AppointmentSchedule.date == form.date.data)

        has_staging = False
        if appointment.first():
            for r in appointment.first().medical_registrations:
                if r.staging:
                    has_staging = True
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
                or len(appointment.first().medical_registrations) < policy.value
            ),
            can_edit=form.date.data >= date.today(),
            can_create=form.date.data >= date.today() and has_staging,
        )


class MedicalRegistrationView(ListPatientView, NurseView):
    def is_accessible(self):
        return NurseView().is_accessible()

    statuses = [
        MedicalRegistrationStatus.SCHEDULED,
        MedicalRegistrationStatus.ARRIVED,
        MedicalRegistrationStatus.CANCELED,
    ]

    def filter(self, appointment):
        return MedicalRegistration.query.filter(
            MedicalRegistration.appointment_schedule_id == appointment.id,
            MedicalRegistration.status.in_(self.statuses),
        )


dashboard.add_view(
    AppointmentScheduleView(
        name="Lập danh sách khám bệnh",
        menu_icon_type="fa",
        menu_icon_value=" fa-user-nurse",
        endpoint="appointment-schedule",
    )
)
dashboard.add_view(
    MedicalRegistrationView(
        name="Danh sách ca khám",
        menu_icon_type="fa",
        menu_icon_value="fa-address-book",
        endpoint="medical-registrations",
    )
)
dashboard.add_view(
    MedicalRegisterView(
        name="Đăng ký khám bệnh",
        menu_icon_type="fa",
        menu_icon_value=" fa-pen-to-square",
        endpoint="medical-register",
    )
)
