from flask import render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from flask_admin import expose
from sqlalchemy import or_

from ..utils import format_money
from ..patient.views import ListPatientView
from .forms import PayBillForm, SearchBillForm
from .. import db
from ..decorators import roles_required
from ..models import (
    Policy,
    AccountRole,
    MedicalExamination,
    User,
    MedicalRegistrationStatus,
    MedicalRegistration,
    Bill,
)
from ..dashboard import ProtectedView, dashboard


class CashierView(ProtectedView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_cashier


class PayBillView(CashierView):
    def is_visible(self):
        return False

    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = PayBillForm()
        medical_registration_id = request.args.get("mid", type=int)
        medical_examination = MedicalExamination.query.filter(
            MedicalExamination.medical_registration_id == medical_registration_id
        ).first()
        examination_fee_policy = Policy.query.get("so-tien-kham")
        if not medical_examination:
            flash("Không tìm thấy ca khám.", category="danger")
            return redirect(url_for("farewell-patients.index"))
        examination_fee_policy = examination_fee_policy.value
        medicine_fee = sum(
            (detail.medicine.price / detail.medicine.quantity) * detail.quantity
            for detail in medical_examination.medical_examination_details
        )
        if form.validate_on_submit():
            bill = Bill(
                amount=examination_fee_policy + medicine_fee,
                fulfilled=True,
                patient_id=medical_examination.medical_registration.patient.id,
                cashier_id=current_user.id,
                medical_examination_id=medical_examination.id,
            )
            medical_examination.medical_registration.status = (
                MedicalRegistrationStatus.COMPLETED
            )
            db.session.add(bill)
            db.session.commit()
        return self.render(
            "cashier/pay_bill.html",
            form=form,
            patient=medical_examination.medical_registration.patient,
            medical_examination=medical_examination,
            examination_fee_policy=format_money(examination_fee_policy),
            medicine_fee=format_money(medicine_fee),
            sum_fee=format_money(examination_fee_policy + medicine_fee),
        )


class BillView(CashierView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = SearchBillForm()
        if not form.id.data:
            form.id.data = ""
        bills = None
        pagination = None
        page = request.args.get("page", 1, type=int)
        pagination = (
            Bill.query.filter(Bill.id.contains(form.id.data))
            .order_by(Bill.id)
            .paginate(
                page=page,
                per_page=current_app.config["ITEMS_PER_PAGE"],
                error_out=False,
            )
        )
        bills = pagination.items
        return self.render(
            "cashier/bill.html",
            form=form,
            bills=bills,
            pagination=pagination,
        )


class FarewellView(ListPatientView, CashierView):
    def is_accessible(self):
        return CashierView().is_accessible()

    statuses = [
        MedicalRegistrationStatus.UNPAID,
        MedicalRegistrationStatus.COMPLETED,
    ]

    def filter(self, appointment):
        return MedicalRegistration.query.filter(
            MedicalRegistration.appointment_schedule_id == appointment.id,
            MedicalRegistration.status.in_(self.statuses),
        )


dashboard.add_view(
    FarewellView(
        name="Danh sách ca khám",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="farewell-patients",
    )
)
dashboard.add_view(
    PayBillView(
        name="Thanh toán hóa đơn",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="pay-bill",
    )
)
dashboard.add_view(
    BillView(
        name="Tra cứu hoá đơn",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="bills",
    )
)
