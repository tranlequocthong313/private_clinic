import sys

sys.path.append("..")

from flask_admin import Admin, expose
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request, render_template
from flask_admin import AdminIndexView, BaseView
from . import db
from manage import app

from app.models import (
    Medicine,
    MedicineType,
    MedicineUnit,
    Medicine_MedicineType,
    Policy,
    User,
    AccountRole,
)


class ProtectedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("main.index"))

    @expose("/")
    def index(self):
        return super(ProtectedView, self).index_view()


class CustomModelView(ProtectedView, ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    can_export = True
    can_view_details = True


class PolicyModelView(CustomModelView):
    form_columns = ["id", "name", "value"]


class UserModelView(CustomModelView):
    column_list = [
        "id",
        "name",
        "email",
        "phone_number",
        "gender",
        "date_of_birth",
        "address",
        "role",
        "confirmed",
        "created_at",
    ]
    form_columns = [
        "name",
        "email",
        "phone_number",
        "name",
        "gender",
        "date_of_birth",
        "address",
        "password_hash",
        "role",
        "confirmed",
    ]


class MedicineUnitModelView(CustomModelView):
    column_list = ["id", "name"]
    form_columns = ["id", "name"]


class MedicineModelView(CustomModelView):
    column_list = [
        "id",
        "name",
        "quantity",
        "manufacturing_date",
        "expiry_date",
        "price",
        "description",
        "medicine_unit",
        "medicine_types",
    ]
    form_columns = [
        "id",
        "name",
        "quantity",
        "manufacturing_date",
        "expiry_date",
        "price",
        "description",
        "medicine_unit",
    ]


class MedicineTypeModelView(CustomModelView):
    column_list = [
        "id",
        "name",
    ]
    form_columns = [
        "name",
    ]


class Medicine_MedicineTypeModelView(CustomModelView):
    column_list = ["id", "medicine", "medicine_type"]
    form_columns = ["medicine", "medicine_type"]


class StatsView(ProtectedView):
    @expose("/")
    def index(self):
        return self.render("admin/stats.html")


dashboard = Admin(
    app,
    name="Admin",
    template_mode="bootstrap4",
    url="/dashboard",
)

dashboard.add_view(
    UserModelView(
        User,
        db.session,
        name="Người dùng",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
    )
)
dashboard.add_view(
    PolicyModelView(
        Policy,
        db.session,
        name="Chính sách",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
    )
)
dashboard.add_view(
    MedicineModelView(
        Medicine,
        db.session,
        name="Thuốc",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="medicines",
    )
)
dashboard.add_view(
    MedicineUnitModelView(
        MedicineUnit,
        db.session,
        name="Đơn vị thuốc",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
    )
)
dashboard.add_view(
    MedicineTypeModelView(
        MedicineType,
        db.session,
        name="Loại thuốc",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
    )
)
dashboard.add_view(
    Medicine_MedicineTypeModelView(
        Medicine_MedicineType,
        db.session,
        name="Thuốc thuộc Loại thuốc",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
    )
)
dashboard.add_view(
    StatsView(
        name="Thống kê",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="stats",
    )
)

from .doctor.views import *
from .nurse.views import *
from .cashier.views import *
from .patient.views import *
from .medicine.views import *
