from flask import render_template
from flask_login import login_required

from . import doctor
from .forms import MedicalForm
from .. import db
from ..decorators import roles_required
from ..models import AccountRole, MedicalExamination, User


@doctor.route("/medical-form", methods=["GET", "POST"])
@login_required
@roles_required([AccountRole.DOCTOR])
def medical_form():
    form = MedicalForm()

    if form.validate_on_submit():
        u = get_user_by_phone(form.phone.data)
        medical_examination = MedicalExamination(
            patient_id=4,
            doctor_id=3,
            symptom=form.symptom.data,
            diagnosis=form.diagnosis.data
        )
        db.session.add(medical_examination)
        db.session.commit()
    return render_template("medical_form.html", form=form)


def get_user_by_phone(phone):
        return User.query.filter.get(User.phone_number.__eq__(phone))
