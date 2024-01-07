import os
from io import BytesIO
from flask import (
    render_template,
    send_file,
    redirect,
    url_for,
    request,
    flash,
    current_app,
    make_response,
)
from flask_login import login_required, current_user
from flask_admin import expose
from datetime import datetime, date
from sqlalchemy import or_

from ..pdf import make_pdf_from_html
from ..patient.views import ListPatientView
from .forms import MedicalExaminationForm
from ..main.forms import SearchingMedicalRegistrationForm
from ..medicine.forms import SearchingMedicineForm
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
from ..dashboard import DashboardView, dashboard
from ..api.views import get_medicines_by_type


class DoctorView(DashboardView):
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
        if not medical_registration_id:
            return redirect(url_for("encounter-patient.index"))

        medical_registration = MedicalRegistration.query.get(medical_registration_id)
        medical_examination = MedicalExamination.query.filter(
            MedicalExamination.id == medical_registration_id
        ).first()
        if (
            medical_registration
            and not medical_examination
            or not medical_examination.fulfilled
        ):
            medical_registration.status = MedicalRegistrationStatus.IN_PROGRESS
            db.session.commit()
        if medical_examination:
            if not form.diagnosis.data:
                form.diagnosis.data = medical_examination.diagnosis
            if not form.advice.data:
                form.advice.data = medical_examination.advice
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
                    id=medical_registration.id,
                    diagnosis=form.diagnosis.data,
                    advice=form.advice.data,
                    patient_id=medical_registration.patient.id,
                    doctor_id=current_user.id,
                    fulfilled=form.submit.data,
                )
                db.session.add(medical_examination)
            else:
                MedicalExaminationDetail.query.filter(
                    MedicalExaminationDetail.medical_examination_id
                    == medical_examination.id
                ).delete()
                medical_examination.advice = form.advice.data
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
            return redirect(
                url_for("medical-examination.index", mid=medical_registration_id)
            )

        medicines = []
        medicine_types = MedicineType.query.all()
        try:
            if not form.medicine_type.data:
                form.medicine_type.data = medicine_types[0].name
            medicines = get_medicines_by_type(form.medicine_type.data)
        except Exception as e:
            print(str(e))
            flash(str(e), category="danger")

        return self.render(
            "doctor/medical_examination.html",
            form=form,
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


class EncounterPatientView(ListPatientView, DoctorView):
    def is_accessible(self):
        return DoctorView().is_accessible()

    statuses = [
        MedicalRegistrationStatus.ARRIVED,
        MedicalRegistrationStatus.IN_PROGRESS,
        MedicalRegistrationStatus.UNPAID,
        MedicalRegistrationStatus.COMPLETED,
    ]

    def filter(self, appointment):
        return MedicalRegistration.query.filter(
            MedicalRegistration.appointment_schedule_id == appointment.id,
            MedicalRegistration.doctor_id == current_user.id,
            MedicalRegistration.status.in_(self.statuses),
        )


class ExportMedicalExaminationPDFView(DoctorView):
    def is_visible(self):
        return False

    @expose("/", methods=["GET"])
    def index(self):
        medical_examination_id = request.args.get("mei", type=int)
        if not medical_examination_id:
            flash("Có lỗi xảy ra.", category="danger")
            return redirect(url_for("medical-examination.index"))
        medical_examination = MedicalExamination.query.get(medical_examination_id)
        if not medical_examination.fulfilled:
            flash("Có lỗi xảy ra.", category="danger")
            return redirect(url_for("medical-examination.index"))
        pdf = make_pdf_from_html(
            "doctor/pdf/medical_examination_pdf.html",
            medical_examination=medical_examination,
            medical_registration=medical_examination.medical_registration,
            patient=medical_examination.medical_registration.patient,
        )
        filename = f"medical_examination_{date.today()}.pdf"
        pdf_path = os.path.join(current_app.config.get("UPLOAD_FOLDER"), filename)
        with open(pdf_path, "wb") as temp_file:
            temp_file.write(pdf)
        bytes_from_file = None
        with open(pdf_path, "rb") as f:
            bytes_from_file = bytearray(f.read())
        res = send_file(
            BytesIO(bytes_from_file),
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf",
        )
        os.remove(os.path.join(current_app.config.get("UPLOAD_FOLDER"), filename))
        return res


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
    ExportMedicalExaminationPDFView(
        name="Xuất phiếu khám",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="export-medical-examination-pdf",
    )
)
