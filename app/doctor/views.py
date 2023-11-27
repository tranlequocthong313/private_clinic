from flask import render_template
from flask_login import login_required

from . import doctor
from .forms import MedicalForm
from ..decorators import roles_required
from ..models import AccountRole


@doctor.route("/medical-form", methods=["GET", "POST"])
@login_required
@roles_required([AccountRole.DOCTOR])
def medical_form():
    form = MedicalForm()
    if form.validate_on_submit():
        # Thuc hien tao phieu kham benh va cac logic khac
        pass
    return render_template("medical_form.html", form=form)
