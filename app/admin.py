import sys

sys.path.append("..")

from flask_admin import Admin
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request
from flask_admin import AdminIndexView
from . import db
from manage import app

from app.models import (
    Medicine,
    MedicineType,
    MedicineUnit,
    Policy,
    User,
    AccountRole,
)


class CustomModelView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    can_export = True
    can_view_details = True

    def is_accessible(self):
        print(current_user.is_authenticated)
        print(current_user.role)
        return current_user.is_authenticated and current_user.role == AccountRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login", next=request.url))


admin = Admin(app, name="Admin", template_mode="bootstrap4")

admin.add_view(
    ModelView(
        User,
        db.session,
        name="Người dùng",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
    )
)
admin.add_view(
    ModelView(
        Policy,
        db.session,
        name="Chính sách",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
    )
)
# admin.add_view(
#     ModelView(
#         Medicine,
#         db.session,
#         name="Thuốc",
#         menu_icon_type="fa",
#         menu_icon_value="fa-users",
#     )
# )
admin.add_view(
    ModelView(
        MedicineUnit,
        db.session,
        name="Đơn vị thuốc",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
    )
)
admin.add_view(
    ModelView(
        MedicineType,
        db.session,
        name="Loại thuốc",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
    )
)
