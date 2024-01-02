from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from flask_admin import expose
from datetime import datetime, date
from sqlalchemy import or_

from .forms import MedicalExaminationForm
from ..main.forms import SearchingMedicalRegistrationForm
from .. import db
from ..decorators import roles_required
from ..models import (
    Medicine,
    MedicineType,
    AccountRole,
    MedicalExamination,
    User,
    MedicalRegistrationStatus,
    MedicalRegistration,
    AppointmentSchedule,
    Policy,
    MedicalExaminationDetail,
)
from ..dashboard import ProtectedView, dashboard
from ..api.views import get_medicines_by_type


class DoctorView(ProtectedView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_doctor


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
        form = MedicalExaminationForm()

        medical_registration_id = request.args.get("mid", type=int)
        patient_id = request.args.get("pid", type=int)
        if not medical_registration_id or not patient_id:
            return redirect(url_for("encounter-patient.index"))

        patient = User.query.get(patient_id)
        medical_registration = MedicalRegistration.query.get(medical_registration_id)
        medical_examination = MedicalExamination.query.filter(
            MedicalExamination.medical_registration_id == medical_registration_id
        ).first()
        if (
            medical_registration
            and not medical_examination
            or not medical_examination.fulfilled
        ):
            medical_registration.status = MedicalRegistrationStatus.IN_PROGRESS
        if medical_examination:
            if not form.diagnosis.data:
                form.diagnosis.data = medical_examination.diagnosis
            if not form.medicines.data:
                for detail in medical_examination.medical_examination_details:
                    form.medicines.append_entry(
                        {
                            "medicine_id": detail.medicine.id,
                            "medicine_name": detail.medicine.name,
                            "unit": detail.medicine.medicine_unit.name,
                            "quantity": detail.quantity,
                            "dosage": detail.dosage,
                        }
                    )

        validating = True

        # - WTF Form's docs: "Do not resize the entries list directly,
        # this will result in undefined behavior. See append_entry and
        # pop_entry for ways you can manipulate the list."
        for i, detail in enumerate(form.medicines):
            if detail.delete_medicine.data:
                del form.medicines.entries[i]
                validating = False
                break

        if form.add_medicine.data:
            medicine = Medicine.query.filter(
                Medicine.name == form.medicine_name.data
            ).first()
            if medicine:
                if medicine.id in [m["medicine_id"] for m in form.medicines.data]:
                    flash(f"{medicine.name} đã có trong đơn thuốc", category="danger")
                else:
                    form.medicines.append_entry(
                        {
                            "medicine_id": medicine.id,
                            "medicine_name": medicine.name,
                            "unit": medicine.medicine_unit.name,
                        }
                    )
        elif form.validate_on_submit() and validating:
            if not medical_examination:
                medical_examination = MedicalExamination(
                    diagnosis=form.diagnosis.data,
                    patient_id=medical_registration.patient.id,
                    doctor_id=current_user.id,
                    medical_registration_id=medical_registration.id,
                    fulfilled=form.submit.data,
                )
                db.session.add(medical_examination)
            else:
                MedicalExaminationDetail.query.filter(
                    MedicalExaminationDetail.medical_examination_id
                    == medical_examination.id
                ).delete()
                medical_examination.diagnosis = form.diagnosis.data
                medical_examination.fulfilled = form.submit.data
            db.session.commit()
            for detail in form.medicines.data:
                medical_examination_detail = MedicalExaminationDetail(
                    medical_examination_id=medical_examination.id,
                    medicine_id=detail["medicine_id"],
                    quantity=detail["quantity"],
                    dosage=detail["dosage"],
                )
                db.session.add(medical_examination_detail)
            if medical_examination.fulfilled:
                medical_registration.status = MedicalRegistrationStatus.UNPAID
            db.session.commit()

            message = "Lập phiếu khám thành công."
            category = "success"
            if form.draft.data:
                message = "Lưu nháp thành công"
                category = "info"
            flash(message, category)

        medicines = []
        medicine_types = MedicineType.query.all()
        try:
            if not form.medicine_type.data:
                form.medicine_type.data = medicine_types[0].name
            medicines = get_medicines_by_type(form.medicine_type.data)
        except Exception as e:
            print(str(e))

        return self.render(
            "doctor/medical_examination.html",
            form=form,
            patient=patient,
            medical_registration=medical_registration,
            dosages=self.dosages,
            medicine_types=medicine_types,
            medicines=medicines,
            medical_examination=medical_examination,
            readonly=True
            if medical_examination and medical_examination.fulfilled
            else False,
            date=date.today(),
            active_tab="examination",
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


class DiseaseHistoryView(DoctorView):
    def is_visible(self):
        return False

    @expose("/", methods=["GET", "POST"])
    def index(self):
        medical_registration_id = request.args.get("mid", type=int)
        patient_id = request.args.get("pid", type=int)
        medical_examinations = MedicalExamination.query.filter(
            MedicalExamination.patient_id == patient_id,
            MedicalExamination.fulfilled == True,
        ).all()
        medical_registration = MedicalRegistration.query.get(medical_registration_id)
        return self.render(
            "doctor/disease_history.html",
            medical_examinations=medical_examinations,
            medical_registration=medical_registration,
            active_tab="history",
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

dashboard.add_view(
    DiseaseHistoryView(
        name="Lịch sử bệnh",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="disease-history",
    )
)
