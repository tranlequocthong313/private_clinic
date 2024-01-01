from flask import render_template, request, current_app
from flask_login import login_required, current_user
from flask_admin import expose
from sqlalchemy import or_

from . import medicine
from .forms import SearchingMedicineForm
from ..decorators import roles_required
from ..models import AccountRole, Medicine
from ..dashboard import ProtectedView, dashboard


class MedicineView(ProtectedView):
    def is_accessible(self):
        return current_user.is_authenticated and (
            current_user.is_doctor() or current_user.is_nurse()
        )

    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = SearchingMedicineForm()
        medicines = None
        pagination = None
        if form.validate_on_submit():
            page = request.args.get("page", 1, type=int)
            pagination = (
                Medicine.query.filter(
                    or_(
                        Medicine.id == form.id.data,
                        Medicine.name == form.name.data,
                    ),
                )
                .order_by(Medicine.created_at.desc())
                .paginate(
                    page=page,
                    per_page=current_app.config["ITEMS_PER_PAGE"],
                    error_out=False,
                )
            )
            medicines = pagination.items
        form.id.data = ""
        form.name.data = ""
        return self.render(
            "medicine/list_medicines.html",
            form=form,
            medicines=medicines,
            pagination=pagination,
        )


dashboard.add_view(
    MedicineView(
        name="Tra cứu thuốc",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="search-medicines",
    )
)
