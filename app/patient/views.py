from flask import render_template, request, current_app
from flask_login import login_required, current_user
from flask_admin import expose
from sqlalchemy import or_
from datetime import date

from .forms import SearchingPatientForm
from ..decorators import roles_required, confirmed_required
from ..models import (
    AccountRole,
    PolicyType,
    User,
    AppointmentSchedule,
    MedicalRegistration,
    Policy,
    MedicalExamination,
)
from ..dashboard import DashboardView, dashboard
from ..main.forms import SearchingMedicalRegistrationForm


class PatientView(DashboardView):
    def is_accessible(self):
        return current_user.is_authenticated and (
            current_user.is_doctor or current_user.is_nurse
        )

    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = SearchingPatientForm()
        patients = None
        pagination = None
        page = request.args.get("page", 1, type=int)
        if not form.keyword.data:
            form.keyword.data = ""
        pagination = (
            User.query.filter(
                or_(
                    User.id == form.keyword.data,
                    User.name.contains(form.keyword.data),
                    User.email.contains(form.keyword.data),
                    User.phone_number.contains(form.keyword.data),
                ),
            )
            .order_by(User.name)
            .paginate(
                page=page,
                per_page=current_app.config["ITEMS_PER_PAGE"],
                error_out=False,
            )
        )
        patients = pagination.items
        return self.render(
            "patient/search_patients.html",
            form=form,
            patients=patients,
            pagination=pagination,
        )


class ListPatientView(PatientView):
    def filter(self, appointment):
        pass

    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = SearchingMedicalRegistrationForm()
        page = request.args.get("page", 1, type=int)
        appointment = AppointmentSchedule.query.filter(
            AppointmentSchedule.date == date.today()
        ).first()
        policy = Policy.query.filter(Policy.type == PolicyType.NUMBER_OF_PATIENTS).first()
        pagination = None
        total_registered_count = 0
        if appointment:
            q = self.filter(appointment)
            total_registered_count = q.count()
            if form.validate_on_submit():
                q = q.join(User, MedicalRegistration.patient_id == User.id).filter(
                    or_(
                        User.id == form.search.data,
                        User.name.contains(form.search.data),
                        User.email.contains(form.search.data),
                        User.phone_number.contains(form.search.data),
                    )
                )
            pagination = q.paginate(
                page=page,
                per_page=current_app.config["ITEMS_PER_PAGE"],
                error_out=False,
            )

        return self.render(
            "medical_registrations.html",
            policy=policy,
            registrations=pagination.items if pagination else None,
            total_registered_count=total_registered_count,
            pagination=pagination,
            statuses=self.statuses,
            date=date.today(),
            form=form,
        )


class DiseaseHistoryView(PatientView):
    def is_visible(self):
        return False

    @expose("/", methods=["GET", "POST"])
    def index(self):
        medical_registration_id = request.args.get("mid", type=int)
        patient_id = request.args.get("pid", type=int)
        medical_registration = MedicalRegistration.query.get(medical_registration_id)
        if medical_registration:
            patient_id = medical_registration.patient.id
        medical_examinations = MedicalExamination.query.filter(
            MedicalExamination.patient_id == patient_id,
            MedicalExamination.fulfilled == True,
        ).all()
        return self.render(
            "disease_history.html",
            medical_examinations=medical_examinations,
            medical_registration=medical_registration,
            active_tab="history",
        )


dashboard.add_view(
    DiseaseHistoryView(
        name="Lịch sử bệnh",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="disease-history",
    )
)


dashboard.add_view(
    PatientView(
        name="Tra cứu bệnh nhân",
        menu_icon_type="fa",
        menu_icon_value="fa-magnifying-glass",
        endpoint="search-patients",
    )
)
