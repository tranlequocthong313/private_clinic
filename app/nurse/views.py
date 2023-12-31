from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_admin import expose
from sqlalchemy import func, or_, desc, case, asc
from datetime import date, datetime

from . import nurse
from .forms import AppointmentDateForm, SearchingMedicalRegistrationForm
from ..main.forms import MedicalRegisterForm
from ..decorators import roles_required
from ..models import (
    AccountRole,
    User,
    MedicalRegistration,
    TimeToVisit,
    AppointmentSchedule,
    Policy,
    MedicalRegistrationStatus,
)
from ..dashboard import ProtectedView, dashboard
from ..utils import random_password
from ..auth.views import register_handler
from ..sms import send_sms
from ..email import send_email
from .. import db
from ..main.views import register_medical


class NurseView(ProtectedView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_nurse()


class MedicalRegisterView(NurseView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = MedicalRegisterForm()
        if form.validate_on_submit():
            register_medical(form)
            return redirect(url_for(".index"))
        return self.render("medical_register.html", form=form)


class AppointmentScheduleView(NurseView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = AppointmentDateForm()
        medical_registrations = MedicalRegistration.query
        appointment = AppointmentSchedule.query
        policy = Policy.query.get("so-benh-nhan")
        medical_registrations = medical_registrations.filter(
            func.date(MedicalRegistration.date_of_visit) <= form.date.data,
            MedicalRegistration.status == MedicalRegistrationStatus.VERIFIED,
        ).order_by(MedicalRegistration.date_of_visit)
        appointment = appointment.filter(AppointmentSchedule.date == form.date.data)

        all_scheduled = True
        if appointment.first():
            for r in appointment.first().medical_registrations:
                if not r.scheduled():
                    all_scheduled = False
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
            can_create=form.date.data >= date.today() and not all_scheduled,
        )


class MedicalRegistrationView(NurseView):
    nurse_concerned_statuses = [
        MedicalRegistrationStatus.SCHEDULED,
        MedicalRegistrationStatus.ARRIVED,
        MedicalRegistrationStatus.CANCELED,
    ]

    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = SearchingMedicalRegistrationForm()
        page = request.args.get("page", 1, type=int)
        per_page = 10
        appointment = AppointmentSchedule.query.filter(
            AppointmentSchedule.date == date.today()
        ).first()
        policy = Policy.query.get("so-benh-nhan")
        pagination = None
        total_registered_count = 0
        if appointment:
            q = MedicalRegistration.query.filter(
                MedicalRegistration.appointment_schedule_id == appointment.id,
                MedicalRegistration.status.in_(self.nurse_concerned_statuses),
            )
            total_registered_count = q.count()
            if form.validate_on_submit():
                q = q.join(User, MedicalRegistration.patient_id == User.id).filter(
                    or_(
                        User.id == form.search.data,
                        User.name.like(f"%{form.search.data}%"),
                        User.email.like(f"%{form.search.data}%"),
                        User.phone_number.like(f"%{form.search.data}%"),
                    )
                )
            pagination = q.paginate(page=page, per_page=per_page, error_out=False)

        return self.render(
            "nurse/medical_registrations.html",
            policy=policy,
            registrations=pagination.items,
            total_registered_count=total_registered_count,
            pagination=pagination,
            statuses=self.nurse_concerned_statuses,
            date=date.today(),
            form=form,
        )


dashboard.add_view(
    AppointmentScheduleView(
        name="Lập danh sách khám bệnh",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="appointment-schedule",
    )
)
dashboard.add_view(
    MedicalRegistrationView(
        name="Danh sách ca khám",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="medical-registrations",
    )
)
dashboard.add_view(
    MedicalRegisterView(
        name="Đăng ký khám bệnh",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="medical-register",
    )
)
