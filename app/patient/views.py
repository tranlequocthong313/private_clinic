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
        page = request.args.get("page", 1, type=int)
        if not form.keyword.data:
            form.keyword.data = ""
        pagination = (
            User.query.filter(
                or_(
                    User.id == form.keyword.data,
                    User.name.like(f"%{form.keyword.data}%"),
                    User.email.like(f"%{form.keyword.data}%"),
                    User.phone_number.like(f"%{form.keyword.data}%"),
                ),
            )
            .order_by(User.name)
            .paginate(
                page=page,
                per_page=current_app.config["ITEMS_PER_PAGE"],
                error_out=False,
            )
        )
        patients = pagination.items
        return self.render(
            "patient/search_patients.html",
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
