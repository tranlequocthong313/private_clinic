from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from flask_admin import expose

from .forms import MedicalForm
from .. import db
from ..decorators import roles_required
from ..models import AccountRole, MedicalExamination, User
from ..admin import ProtectedView, admin


class CashierView(ProtectedView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_cashier()


class PayBillView(CashierView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        return self.render("cashier/pay_bill.html")


class BillView(CashierView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        return self.render("cashier/bill.html")


admin.add_view(
    PayBillView(
        name="Thanh toán hóa đơn",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="pay-bill",
    )
)
admin.add_view(
    BillView(
        name="Tra cứu hoá đơn",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="bills",
    )
)
