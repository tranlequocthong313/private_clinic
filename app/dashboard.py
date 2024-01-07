import sys

sys.path.append("..")

from flask_admin import Admin, expose
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request, render_template
from flask_admin import AdminIndexView, BaseView
from . import db
from manage import app
from sqlalchemy import extract

from app.models import (
    Medicine,
    MedicineType,
    MedicineUnit,
    Medicine_MedicineType,
    Policy,
    User,
    AccountRole,
)


class HomeView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login"))

    @expose("/")
    def index(self):
        return self.render("admin/index.html")


class DashboardView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin.index"))

    @expose("/")
    def index(self):
        return super(DashboardView, self).index_view()


class CustomModelView(DashboardView, ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    can_export = True
    can_view_details = True


class PolicyModelView(CustomModelView):
    form_columns = ["name", "value", "type"]


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
    form_columns = ["name"]


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


class StatsView(DashboardView):
    @expose("/")
    def index(self):
        date_object = datetime.strptime(
            request.args.get("month", f"{date.today().year}-{date.today().month}"),
            "%Y-%m",
        )
        year = date_object.year
        month = date_object.month
        stats = (
            db.session.query(
                extract("day", Bill.created_at).label("day"),
                func.sum(Bill.amount).label("total_revenue"),
                func.count().label("total_examinations"),
            )
            .filter(
                Bill.fulfilled == True,
                extract("month", Bill.created_at) == month,
                extract("year", Bill.created_at) == year,
            )
            .group_by("day")
            .order_by("day")
            .all()
        )
        return self.render(
            "admin/stats.html",
            stats=stats,
            month=month if month > 9 else f"0{month}",
            year=year,
            total_revenue_of_the_month=sum([stat[1] for stat in stats]),
            total_examinations_of_the_month=sum([stat[2] for stat in stats]),
            active_tab="revenue",
        )


class MedicineStatsView(DashboardView):
    def is_visible(self):
        return False

    @expose("/")
    def index(self):
        date_object = datetime.strptime(
            request.args.get("month", f"{date.today().year}-{date.today().month}"),
            "%Y-%m",
        )
        year = date_object.year
        month = date_object.month
        stats = (
            db.session.query(
                Medicine.name,
                MedicineUnit.name,
                Medicine.quantity,
                func.sum(MedicalExaminationDetail.quantity).label("total_quantity"),
            )
            .join(MedicineUnit)
            .join(MedicalExaminationDetail)
            .join(MedicalExamination)
            .filter(
                extract("month", MedicalExamination.created_at) == month,
                extract("year", MedicalExamination.created_at) == year,
                MedicalExamination.fulfilled == True,
            )
            .group_by(Medicine.name)
            .all()
        )

        return self.render(
            "admin/medicine_stats.html",
            stats=stats,
            month=month if month > 9 else f"0{month}",
            year=year,
            active_tab="medicine",
        )


class ExportStatsPDFView(DashboardView):
    def is_visible(self):
        return False

    @expose("/", methods=["GET"])
    def index(self):
        date_object = datetime.strptime(
            request.args.get("month", f"{date.today().year}-{date.today().month}"),
            "%Y-%m",
        )
        year = date_object.year
        month = date_object.month
        stats = (
            db.session.query(
                extract("day", Bill.created_at).label("day"),
                func.sum(Bill.amount).label("total_revenue"),
                func.count().label("total_examinations"),
            )
            .filter(
                Bill.fulfilled == True,
                extract("month", Bill.created_at) == month,
                extract("year", Bill.created_at) == year,
            )
            .group_by("day")
            .order_by("day")
            .all()
        )
        pdf = make_pdf_from_html(
            "admin/pdf/stats_pdf.html",
            stats=stats,
            month=month if month > 9 else f"0{month}",
            year=year,
            total_revenue_of_the_month=sum([stat[1] for stat in stats]),
            total_examinations_of_the_month=sum([stat[2] for stat in stats]),
        )
        filename = f"stats_{month}-{year}.pdf"
        pdf_path = os.path.join(current_app.config.get("UPLOAD_FOLDER"), filename)
        with open(pdf_path, "wb") as temp_file:
            temp_file.write(pdf)
        bytes_from_file = None
        with open(pdf_path, "rb") as f:
            bytes_from_file = bytearray(f.read())
        res = send_file(
            BytesIO(bytes_from_file),
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf",
        )
        os.remove(os.path.join(current_app.config.get("UPLOAD_FOLDER"), filename))
        return res


class ExportMedicineStatsPDFView(DashboardView):
    def is_visible(self):
        return False

    @expose("/", methods=["GET"])
    def index(self):
        date_object = datetime.strptime(
            request.args.get("month", f"{date.today().year}-{date.today().month}"),
            "%Y-%m",
        )
        year = date_object.year
        month = date_object.month
        stats = (
            db.session.query(
                Medicine.name,
                MedicineUnit.name,
                Medicine.quantity,
                func.sum(MedicalExaminationDetail.quantity).label("total_quantity"),
            )
            .join(MedicineUnit)
            .join(MedicalExaminationDetail)
            .join(MedicalExamination)
            .filter(
                extract("month", MedicalExamination.created_at) == month,
                extract("year", MedicalExamination.created_at) == year,
                MedicalExamination.fulfilled == True,
            )
            .group_by(Medicine.name)
            .all()
        )
        pdf = make_pdf_from_html(
            "admin/pdf/medicine_stats_pdf.html",
            stats=stats,
            month=month if month > 9 else f"0{month}",
            year=year,
        )
        filename = f"medicine_stats_{month}-{year}.pdf"
        pdf_path = os.path.join(current_app.config.get("UPLOAD_FOLDER"), filename)
        with open(pdf_path, "wb") as temp_file:
            temp_file.write(pdf)
        bytes_from_file = None
        with open(pdf_path, "rb") as f:
            bytes_from_file = bytearray(f.read())
        res = send_file(
            BytesIO(bytes_from_file),
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf",
        )
        os.remove(os.path.join(current_app.config.get("UPLOAD_FOLDER"), filename))
        return res


dashboard = Admin(
    app,
    name="Dashboard",
    template_mode="bootstrap4",
    url="/dashboard",
    index_view=HomeView(),
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
        menu_icon_value="fa-book",
    )
)
dashboard.add_view(
    MedicineModelView(
        Medicine,
        db.session,
        name="Thuốc",
        menu_icon_type="fa",
        menu_icon_value="fa-capsules",
        endpoint="medicines",
    )
)
dashboard.add_view(
    MedicineUnitModelView(
        MedicineUnit,
        db.session,
        name="Đơn vị thuốc",
        menu_icon_type="fa",
        menu_icon_value="fa-prescription-bottle",
    )
)
dashboard.add_view(
    MedicineTypeModelView(
        MedicineType,
        db.session,
        name="Loại thuốc",
        menu_icon_type="fa",
        menu_icon_value="fa-syringe",
    )
)
dashboard.add_view(
    Medicine_MedicineTypeModelView(
        Medicine_MedicineType,
        db.session,
        name="Thuốc thuộc Loại thuốc",
        menu_icon_type="fa",
        menu_icon_value="fa-pills",
    )
)
dashboard.add_view(
    StatsView(
        name="Thống kê",
        menu_icon_type="fa",
        menu_icon_value="fa-chart-simple",
        endpoint="stats",
    )
)
dashboard.add_view(
    MedicineStatsView(
        name="Thống kê tần suất sử dụng thuốc",
        endpoint="medicine-stats",
    )
)
dashboard.add_view(
    ExportStatsPDFView(
        name="Xuất thống kê doanh thu và tần suất khám",
        endpoint="export-revenue-pdf",
    )
)
dashboard.add_view(
    ExportMedicineStatsPDFView(
        name="Xuất thống kê tần suất sử dụng thuốc",
        endpoint="export-medicine-stats-pdf",
    )
)

from .doctor.views import *
from .nurse.views import *
from .cashier.views import *
from .patient.views import *
from .medicine.views import *
