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
    user = get_user_by_phone()
    if form.validate_on_submit():

        medical_examination = MedicalExamination(
            patient_id=4,
            doctor_id=3,
            symptom=form.symptom.data,
            diagnosis=form.diagnosis.data,

        )
        db.session.add(medical_examination)
        db.session.commit()
    return render_template("medical_form.html", form=form, user=user)



def get_user_by_phone():
    return User.query.get(4)
