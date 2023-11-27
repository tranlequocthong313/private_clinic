from flask import render_template, request, current_app
from flask_login import login_required
from sqlalchemy import or_

from . import medicine
from .forms import SearchingMedicineForm
from ..decorators import roles_required
from ..models import AccountRole, Medicine


@medicine.route("/medicines", methods=["GET", "POST"])
@login_required
@roles_required([AccountRole.DOCTOR, AccountRole.NURSE])
def list_medicines():
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
    return render_template(
        "medicine/list_medicines.html",
        form=form,
        medicines=medicines,
        pagination=pagination,
    )
