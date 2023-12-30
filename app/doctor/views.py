from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from flask_admin import expose

from . import doctor
from .forms import MedicalForm, MedicalDetaiForm
from .. import db
from ..decorators import roles_required
from ..models import AccountRole, MedicalExamination, User, medical_examination_detail
from ..admin import ProtectedView, dashboard


class DoctorView(ProtectedView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_doctor()


class MedicalFormView(DoctorView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = MedicalForm()
        form2 = MedicalDetaiForm()
        user = self.__get_user_by_phone()
        if form.validate_on_submit():
            medical_examination = MedicalExamination(
                patient_id=2,
                doctor_id=1,
                symptom=form.symptom.data,
                diagnosis=form.diagnosis.data,
            )
            db.session.add(medical_examination)
            db.session.commit()

        if form2.validate_on_submit():
            medical = medical_examination_detail(
                dosage=form2.dosage.data, quantity=form2.quantity.data
            )
            db.session.add(medical)
            db.session.commit()
        return self.render(
            "doctor/medical_form.html", form=form, user=user, form2=form2
        )

    def __get_user_by_phone(self):
        return User.query.get(4)


dashboard.add_view(
    MedicalFormView(
        name="Lập phiếu khám",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="medical-form",
    )
)
