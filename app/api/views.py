from flask import render_template, request, current_app, jsonify, session
from flask_login import login_required
from sqlalchemy import or_

from . import api
from ..decorators import roles_required
from ..models import AccountRole, Medicine


@api.route("/medicines", methods=["POST"])
@login_required
@roles_required([AccountRole.DOCTOR, AccountRole.NURSE])
def list_medicines():
    body = request.get_json()
    print(body)
    medicine = Medicine.query.filter_by(name=body.get('name')).first()
    print({
        "id": medicine.id,
        "name": medicine.name,
        "unit": medicine.medicine_unit.name,
        "quantity": body.get("quantity"),
        "dosage": body.get("dosage"),
    })

    return jsonify({
        "id": medicine.id,
        "name": medicine.name,
        "unit": medicine.medicine_unit.name,
        "quantity": body.get("quantity"),
        "dosage": body.get("dosage"),
    })
