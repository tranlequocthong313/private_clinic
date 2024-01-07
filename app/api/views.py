from flask import (
    url_for,
    redirect,
    render_template,
    request,
    current_app,
    jsonify,
    session,
    make_response,
    render_template_string,
    flash,
)
from flask_login import login_required, current_user
from sqlalchemy import or_

from ..vnpay import vnpay
from . import api
from ..decorators import roles_required
from ..models import (
    Bill,
    MedicalExamination,
    AccountRole,
    Medicine,
    AppointmentSchedule,
    MedicalRegistration,
    Policy,
    MedicalRegistrationStatus,
    Medicine_MedicineType,
    MedicineType,
)
from .. import db
from ..sms import send_sms
from ..email import send_email


def get_medicines_by_type(type_name):
    medicine_type = MedicineType.query.filter(MedicineType.name == type_name).first()
    if not medicine_type:
        raise Exception("Không tìm thấy loại thuốc.")

    if not medicine_type.medicines:
        raise Exception("Loại thuốc này không có thuốc nào.")
    else:
        medicines = medicine_type.medicines
        return [m.medicine for m in medicines]


@api.route("/medicines", methods=["GET"])
@login_required
@roles_required([AccountRole.DOCTOR])
def search_medicines():
    type_name = request.args.get("type")
    try:
        medicines = get_medicines_by_type(type_name)
        return jsonify(
            {
                "medicines": [
                    {
                        "id": m.id,
                        "name": m.name,
                        "quantity": m.quantity,
                        "price": m.price,
                        "description": m.description,
                        "unit": m.medicine_unit.name,
                    }
                    for m in medicines
                ],
                "message": "Lấy thuốc thành công.",
            }
        )
    except Exception as e:
        return jsonify({"message": str(e)})


@api.route("/appointment-schedule", methods=["POST"])
@login_required
@roles_required([AccountRole.NURSE])
def schedule():
    body = request.get_json()
    appointment_id = (
        AppointmentSchedule.query.filter(AppointmentSchedule.date == body["date"])
        .first()
        .id
    )
    registrations = MedicalRegistration.query.filter(
        MedicalRegistration.appointment_schedule_id == appointment_id
    )

    for r in registrations:
        r = MedicalRegistration.query.get(r.id)
        if r.staging:
            r.status = MedicalRegistrationStatus.SCHEDULED
            if r.patient.phone_number:
                send_sms(
                    r.patient.phone_number,
                    "nurse/sms/appointment_sms",
                    patient=r.patient,
                    registration=r,
                    appointment=r.appointment_schedule,
                )
            if r.patient.email:
                send_email(
                    r.patient.email,
                    "Lịch hẹn khám",
                    "nurse/email/appointment_email",
                    patient=r.patient,
                    registration=r,
                    appointment=r.appointment_schedule,
                )
    db.session.commit()
    return jsonify(
        {
            "message": "Lập danh sách thành công",
        }
    )


@api.route("/medical-registrations/<id>/appointment", methods=["PUT"])
@login_required
@roles_required([AccountRole.NURSE])
def add_to_schedule(id):
    body = request.get_json()
    appointment = AppointmentSchedule.query.filter(
        AppointmentSchedule.date == body["date"]
    ).first()
    if not appointment:
        appointment = AppointmentSchedule(nurse_id=current_user.id, date=body["date"])
        db.session.add(appointment)
    registration = MedicalRegistration.query.get(id)
    registration.appointment_schedule_id = appointment.id
    registration.status = MedicalRegistrationStatus.STAGING
    db.session.commit()

    return jsonify(
        {
            "message": "Thêm vào danh sách thành công",
        }
    )


@api.route("/medical-registrations/<id>/appointment", methods=["DELETE"])
@login_required
@roles_required([AccountRole.NURSE])
def delete_from_schedule(id):
    registration = MedicalRegistration.query.get(id)
    registration.appointment_schedule_id = None
    registration.status = MedicalRegistrationStatus.REGISTERED
    db.session.commit()

    return jsonify(
        {
            "message": "Xóa khỏi danh sách thành công",
        }
    )


@api.route("/medical-registrations/<id>", methods=["DELETE"])
@login_required
@roles_required([AccountRole.NURSE])
def delete_medical_registration(id):
    MedicalRegistration.query.filter(MedicalRegistration.id == id).delete()
    db.session.commit()

    return jsonify(
        {
            "message": "Xóa ca hẹn khám thành công",
        }
    )


@api.route("/medical-registrations/<id>/status", methods=["PUT"])
@login_required
@roles_required([AccountRole.NURSE])
def change_medical_registration_status(id):
    body = request.get_json()
    r = MedicalRegistration.query.get(id)
    r.status = body["status"]
    db.session.commit()

    return jsonify(
        {
            "message": "Thay đổi trạng thái ca khám thành công",
        }
    )
