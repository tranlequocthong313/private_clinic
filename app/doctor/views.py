from flask import render_template
from flask_login import login_required

from . import doctor
from .forms import MedicalForm
from .. import db
from ..decorators import roles_required
from ..models import AccountRole, MedicalExamination


@doctor.route("/medical-form", methods=["GET", "POST"])
@login_required
@roles_required([AccountRole.DOCTOR])
def medical_form():
    form = MedicalForm()
    if form.validate_on_submit():
        medicalExamination = MedicalExamination(
            symptom=form.symptom.data,
            diagnosis=form.diagnosis.data
        )
        db.session.add(medicalExamination)
        db.session.commit()
        pass
    return render_template("medical_form.html", form=form)
