from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from flask_admin import expose
from datetime import datetime, date
from sqlalchemy import or_

from .forms import MedicalExaminationForm
from ..main.forms import SearchingMedicalRegistrationForm
from .. import db
from ..decorators import roles_required
from ..models import (
    MedicineType,
    AccountRole,
    MedicalExamination,
    User,
    medical_examination_detail,
    MedicalRegistrationStatus,
    MedicalRegistration,
    AppointmentSchedule,
    Policy,
)
from ..dashboard import ProtectedView, dashboard


class DoctorView(ProtectedView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_doctor()


class MedicalExaminationView(DoctorView):
    def is_visible(self):
        return False

    dosages = [
        "Sau ăn 30 phút",
        "Trước ăn 30 phút",
        "Ngay sau khi ăn",
        "Khi đói",
        "Trước khi đi ngủ",
        "Ngậm dưới lưỡi",
        "Khi sốt >= 38.5 độ C",
        "Ngày 2 viên chia đều 2 lần sáng tối",
    ]

    @expose("/", methods=["GET", "POST"])
    def index(self):
        medical_registration_id = request.args.get("mid", type=int)
        patient_id = request.args.get("pid", type=int)
        if not medical_registration_id or not patient_id:
            return redirect(url_for("encounter-patient.index"))

        patient = User.query.get(patient_id)
        medical_registration = MedicalRegistration.query.get(medical_registration_id)

        form = MedicalExaminationForm()
        if form.add_medicine.data:
            print("ADD")
            form.medicines.append_entry(None)

        # - WTF Form's docs: "Do not resize the entries list directly,
        # this will result in undefined behavior. See append_entry and
        # pop_entry for ways you can manipulate the list."
        for i, medicine in enumerate(form.medicines):
            if medicine.delete_medicine.data:
                print("DELETE")
                del form.medicines.entries[i]
                break

        print(form.validate_on_submit())
        if form.validate_on_submit():
            print("SUBMIT")
            for medicine in form.medicines.data:
                print(medicine)

        return self.render(
            "doctor/medical_examination.html",
            form=form,
            patient=patient,
            medical_registration=medical_registration,
            dosages=self.dosages,
            medicine_types=MedicineType.query.all(),
        )


class EncounterPatientView(DoctorView):
    doctor_concerned_statuses = [
        MedicalRegistrationStatus.ARRIVED,
        MedicalRegistrationStatus.IN_PROGRESS,
        MedicalRegistrationStatus.COMPLETED,
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
                MedicalRegistration.doctor_id == current_user.id,
                MedicalRegistration.status.in_(self.doctor_concerned_statuses),
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
            "medical_registrations.html",
            policy=policy,
            registrations=pagination.items if pagination else None,
            total_registered_count=total_registered_count,
            pagination=pagination,
            statuses=self.doctor_concerned_statuses,
            date=date.today(),
            form=form,
        )


dashboard.add_view(
    EncounterPatientView(
        name="Danh sách ca khám",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="encounter-patient",
    )
)

dashboard.add_view(
    MedicalExaminationView(
        name="Lập phiếu khám",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="medical-examination",
    )
)
