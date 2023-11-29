from flask import render_template, request, current_app
from flask_login import login_required
from sqlalchemy import or_

from . import patient
from .forms import SearchingPatientForm
from ..decorators import roles_required, confirmed_required
from ..models import AccountRole, User


@patient.route("/patients", methods=["GET", "POST"])
@login_required
@roles_required([AccountRole.DOCTOR, AccountRole.NURSE])
def list_patients():
    form = SearchingPatientForm()
    patients = None
    pagination = None
    if form.validate_on_submit():
        page = request.args.get("page", 1, type=int)
        pagination = (
            User.query.filter(
                User.role == AccountRole.PATIENT,
                or_(
                    User.id == form.id.data,
                    User.email == form.email.data,
                    User.phone_number == form.phone_number.data,
                ),
            )
            .order_by(User.created_at.desc())
            .paginate(
                page=page,
                per_page=current_app.config["ITEMS_PER_PAGE"],
                error_out=False,
            )
        )
        patients = pagination.items
    form.id.data = ""
    form.email.data = ""
    form.phone_number.data = ""
    return render_template(
        "patient/list_patients.html",
        form=form,
        patients=patients,
        pagination=pagination,
    )
