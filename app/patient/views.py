from flask import render_template, request, current_app
from flask_login import login_required, current_user
from flask_admin import expose
from sqlalchemy import or_

from .forms import SearchingPatientForm
from ..decorators import roles_required, confirmed_required
from ..models import AccountRole, User
from ..dashboard import ProtectedView, dashboard


class PatientView(ProtectedView):
    def is_accessible(self):
        return current_user.is_authenticated and (
            current_user.is_doctor or current_user.is_nurse
        )

    @expose("/", methods=["GET", "POST"])
    def index(self):
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
        return self.render(
            "patient/list_patients.html",
            form=form,
            patients=patients,
            pagination=pagination,
        )


dashboard.add_view(
    PatientView(
        name="Tra cứu bệnh nhân",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="search-patients",
    )
)
