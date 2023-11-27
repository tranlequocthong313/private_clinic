# from flask import render_template
# from flask_login import login_required

# from . import nurse
# from .forms import MedicalForm
# from ..decorators import roles_required
# from ..models import AccountRole


# @nurse.route("/medical-form", methods=["GET", "POST"])
# @login_required
# @roles_required([AccountRole.nurse])
# def medical_form():
#     form = MedicalForm()
#     if form.validate_on_submit():
#         # Thuc hien tao phieu kham benh va cac logic khac
#         pass
#     return render_template("medical_form.html", form=form)
