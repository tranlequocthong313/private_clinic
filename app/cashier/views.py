import os
from io import BytesIO
from flask import (
    render_template,
    redirect,
    url_for,
    request,
    flash,
    current_app,
    send_file,
)
from flask_login import login_required, current_user
from flask_admin import expose
from sqlalchemy import or_
from datetime import date

from ..pdf import make_pdf_from_html
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
from ..dashboard import DashboardView, dashboard


class CashierView(DashboardView):
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
        if not medical_examination:
            flash("Không tìm thấy ca khám.", category="danger")
            return redirect(url_for("farewell-patients.index"))
        examination_fee_policy = Policy.query.get("so-tien-kham")
        bill = Bill.query.filter(
            Bill.medical_examination_id == medical_examination.id
        ).first()
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
            flash("Thanh toán hóa đơn thành công.", category="success")
            return redirect(url_for("pay-bill.index", mid=medical_registration_id))
        return self.render(
            "cashier/pay_bill.html",
            form=form,
            bill=bill,
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


class ExportBillPDFView(CashierView):
    def is_visible(self):
        return False

    @expose("/", methods=["GET"])
    def index(self):
        bill_id = request.args.get("bid", type=int)
        if not bill_id:
            flash("Có lỗi xảy ra.", category="danger")
            return redirect(url_for("farewell-patients.index"))
        bill = Bill.query.get(bill_id)
        if not bill.fulfilled:
            flash("Có lỗi xảy ra.", category="danger")
            return redirect(url_for("farewell-patients.index"))
        policy = Policy.query.get("so-tien-kham")
        pdf = make_pdf_from_html(
            "cashier/pdf/pay_bill_pdf.html",
            examination_fee=policy.value,
            total_amount=bill.amount,
            bill=bill,
            medical_examination=bill.medical_examination,
            patient=bill.patient,
            cashier=bill.cashier,
        )
        filename = f"bill_{date.today()}.pdf"
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
dashboard.add_view(
    ExportBillPDFView(
        name="Xuất hóa đơn",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="export-bill-pdf",
    )
)
