import os
from datetime import date
from io import BytesIO

from flask import (
    current_app,
    flash,
    redirect,
    request,
    send_file,
    url_for,
)
from flask_admin import expose
from flask_login import current_user

from .. import db
from ..api.views import get_medicines_by_type
from ..dashboard import DashboardView, dashboard
from ..models import (
    MedicalExamination,
    MedicalExaminationDetail,
    MedicalRegistration,
    MedicalRegistrationStatus,
    Medicine,
    MedicineType,
)
from ..patient.views import ListPatientView
from ..pdf import make_pdf_from_html
from .forms import MedicalExaminationForm


class DoctorView(DashboardView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_doctor


class MedicalExaminationView(DoctorView):
    def is_visible(self):
        return False

    # NOTE: Available example dosages for doctor when creating medical examinations
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

        self.__in_progress(medical_examination, medical_registration)
        self.__fill_form_data(form, medical_examination)

        validating = True
        validating = self.__delete_medicine(form, validating)

        if form.add_medicine.data:
            self.__add_new_medicine(form)
        elif form.validate_on_submit() and validating:
            if not medical_examination:
                medical_examination = self.__create_new_medical_examination(
                    form, medical_examination, medical_registration
                )
            else:
                self.__update_old_medical_examination(form, medical_examination)
            db.session.commit()
            self.__create_new_medical_examination_detail(form, medical_examination)
            self.__finish(medical_examination, medical_registration)
            db.session.commit()
            self.__notify(form)
            return redirect(
                url_for("medical-examination.index", mid=medical_registration_id)
            )

        medicines = []
        medicine_types = MedicineType.query.all()
        medicines = self.__get_medicines_by_type(form, medicine_types, medicines)

        return self.render(
            "doctor/medical_examination.html",
            form=form,
            medical_registration=medical_registration,
            dosages=self.dosages,
            medicine_types=medicine_types,
            medicines=medicines,
            medical_examination=medical_examination,
            readonly=bool(medical_examination and medical_examination.fulfilled),
            date=date.today(),
            active_tab="examination",
        )

    def __in_progress(self, medical_examination, medical_registration):
        if (
            medical_registration
            and not medical_examination
            or not medical_examination.fulfilled
        ):
            medical_registration.status = MedicalRegistrationStatus.IN_PROGRESS
            db.session.commit()

    def __fill_form_data(self, form, medical_examination):
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

    def __add_new_medicine(self, form):
        if medicine := Medicine.query.filter(
            Medicine.name == form.medicine_name.data
        ).first():
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

    def __create_new_medical_examination(
        self, form, medical_examination, medical_registration
    ) -> None:
        medical_examination = MedicalExamination(
            id=medical_registration.id,
            diagnosis=form.diagnosis.data,
            advice=form.advice.data,
            patient_id=medical_registration.patient.id,
            doctor_id=current_user.id,
            fulfilled=form.submit.data,
        )
        db.session.add(medical_examination)
        return medical_examination

    def __update_old_medical_examination(self, form, medical_examination):
        MedicalExaminationDetail.query.filter(
            MedicalExaminationDetail.medical_examination_id == medical_examination.id
        ).delete()
        medical_examination.advice = form.advice.data
        medical_examination.diagnosis = form.diagnosis.data
        medical_examination.fulfilled = form.submit.data

    def __delete_medicine(self, form, validating) -> None:
        # WARNING: WTF Form's docs: "Do not re-size the entries list directly,
        # this will result in undefined behavior. See append_entry and
        # pop_entry for ways you can manipulate the list."
        for i, detail in enumerate(form.medicines):
            if detail.delete_medicine.data:
                del form.medicines.entries[i]
                validating = False
                break
        return validating

    def __create_new_medical_examination_detail(self, form, medical_examination):
        for detail in form.medicines.data:
            medical_examination_detail = MedicalExaminationDetail(
                medical_examination_id=medical_examination.id,
                medicine_id=detail["medicine_id"],
                quantity=detail["quantity"],
                dosage=detail["dosage"],
            )
            db.session.add(medical_examination_detail)

    def __finish(self, medical_examination, medical_registration):
        if medical_examination.fulfilled:
            medical_registration.status = MedicalRegistrationStatus.UNPAID

    def __notify(self, form) -> None:
        message = "Lập phiếu khám thành công."
        category = "success"
        if form.draft.data:
            message = "Lưu nháp thành công"
            category = "info"
        flash(message, category)
        return category

    def __get_medicines_by_type(self, form, medicine_types, medicines) -> None:
        try:
            if not form.medicine_type.data:
                form.medicine_type.data = medicine_types[0].name
            medicines = get_medicines_by_type(form.medicine_type.data)
        except Exception as e:
            print(e)
            flash(str(e), category="danger")
        return medicines


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
