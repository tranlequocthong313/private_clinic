from flask import render_template, request, current_app, jsonify, session, make_response
from flask_login import login_required, current_user
from sqlalchemy import or_

from . import api
from ..decorators import roles_required
from ..models import (
    AccountRole,
    Medicine,
    AppointmentSchedule,
    MedicalRegistration,
    Policy,
    MedicalRegistrationStatus,
)
from .. import db
from ..sms import send_sms
from ..email import send_email


@api.route("/medicines", methods=["POST"])
@login_required
@roles_required([AccountRole.DOCTOR, AccountRole.NURSE])
def list_medicines():
    body = request.get_json()
    medicine = Medicine.query.filter_by(name=body.get("name")).first()

    if medicine:
        return jsonify(
            {
                "id": medicine.id,
                "name": medicine.name,
                "unit": medicine.medicine_unit.name,
                "quantity": body.get("quantity"),
                "dosage": body.get("dosage"),
            }
        )
    else:
        response = jsonify({"error": "bad request", "message": "Medicine not found"})
        response.status_code = 400
        return response


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
        if r.not_scheduled():
            r.status = MedicalRegistrationStatus.SCHEDULED
            if r.patient.phone_number:
                send_sms(r.patient.phone_number, "Lịch khám của bạn là")
            if r.patient.email:
                send_email(
                    r.patient.email,
                    "Lịch khám",
                    "nurse/email/appointment",
                    user=r.patient,
                )
    db.session.commit()
    return jsonify(
        {
            "message": "Lập danh sách thành công",
        }
    )


@api.route("/medical-registrations", methods=["PUT"])
@login_required
@roles_required([AccountRole.NURSE])
def add_to_schedule():
    body = request.get_json()
    appointment = AppointmentSchedule.query.filter(
        AppointmentSchedule.date == body["date"]
    ).first()
    if not appointment:
        appointment = AppointmentSchedule(nurse_id=current_user.id, date=body["date"])
        db.session.add(appointment)
    registration = MedicalRegistration.query.get(body["id"])
    registration.appointment_schedule_id = appointment.id
    db.session.commit()

    return jsonify(
        {
            "message": "Thêm vào danh sách thành công",
        }
    )


@api.route("/appointment/medical-registrations/<id>", methods=["DELETE"])
@login_required
@roles_required([AccountRole.NURSE])
def delete_from_schedule(id):
    registration = MedicalRegistration.query.get(id)
    registration.appointment_schedule_id = None
    registration.status = MedicalRegistrationStatus.NOT_SCHEDULED
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


@api.route("/policies/<id>", methods=["GET"])
@login_required
@roles_required([AccountRole.NURSE])
def get_policies(id):
    policy = Policy.query.get(id)
    return jsonify({"value": policy.value})
