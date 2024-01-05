from flask import render_template, request, current_app
from flask_login import login_required, current_user
from flask_admin import expose
from sqlalchemy import or_

from .forms import SearchingMedicineForm
from ..decorators import roles_required
from ..models import AccountRole, Medicine, MedicalRegistration
from ..dashboard import DashboardView, dashboard


class MedicineView(DashboardView):
    def is_accessible(self):
        return current_user.is_authenticated and (
            current_user.is_doctor or current_user.is_nurse
        )

    @expose("/", methods=["GET", "POST"])
    def index(self):
        medical_registration_id = request.args.get("mid", type=int)
        medical_registration = MedicalRegistration.query.get(medical_registration_id)
        form = SearchingMedicineForm()
        if not form.keyword.data:
            form.keyword.data = ""
        medicines = None
        pagination = None
        page = request.args.get("page", 1, type=int)
        pagination = (
            Medicine.query.filter(
                or_(
                    Medicine.name.contains(form.keyword.data),
                    Medicine.id.contains(form.keyword.data),
                ),
            )
            .order_by(Medicine.name)
            .paginate(
                page=page,
                per_page=current_app.config["ITEMS_PER_PAGE"],
                error_out=False,
            )
        )
        medicines = pagination.items
        return self.render(
            "medicine/search_medicines.html",
            form=form,
            medicines=medicines,
            pagination=pagination,
            active_tab="searching",
            medical_registration=medical_registration,
        )


dashboard.add_view(
    MedicineView(
        name="Tra cứu thuốc",
        menu_icon_type="fa",
        menu_icon_value=" fa-magnifying-glass",
        endpoint="search-medicines",
    )
)
