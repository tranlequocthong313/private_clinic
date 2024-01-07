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
from datetime import date, datetime

from ..vnpay import vnpay
from ..pdf import make_pdf_from_html
from ..utils import format_money
from ..patient.views import ListPatientView
from .forms import PayBillForm, SearchBillForm
from .. import db
from ..decorators import roles_required
from ..models import (
    PolicyType,
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
            MedicalExamination.id == medical_registration_id
        ).first()
        if not medical_examination:
            flash("Không tìm thấy ca khám.", category="danger")
            return redirect(url_for("farewell-patients.index"))
        examination_fee_policy = Policy.query.filter(Policy.type == PolicyType.EXAMINATION_FEE).first()
        bill = Bill.query.filter(
            Bill.id == medical_examination.id
        ).first()
        examination_fee_policy = examination_fee_policy.value
        medicine_fee = sum(
            (detail.medicine.price / detail.medicine.quantity) * detail.quantity
            for detail in medical_examination.medical_examination_details
        )
        if form.validate_on_submit():
            if not bill:
                bill = Bill(
                    id=medical_examination.id,
                    amount=examination_fee_policy + medicine_fee,
                    fulfilled=form.pay_options.data == "cash",
                    patient_id=medical_examination.medical_registration.patient.id,
                    cashier_id=current_user.id,
                )
                db.session.add(bill)
                db.session.commit()
            if form.pay_options.data == "cash":
                medical_examination.medical_registration.status = (
                    MedicalRegistrationStatus.COMPLETED
                )
                bill.fulfilled = True;
                db.session.commit()
                flash("Thanh toán hóa đơn thành công.", category="success")
                return redirect(url_for("pay-bill.index", mid=medical_registration_id))
            elif form.pay_options.data == "vnpay":
                order_type = "billpayment"
                order_id = bill.id
                amount = int(bill.amount)
                order_desc = f"Thanh toán viện phí cho bệnh nhân {bill.patient.name}, với số tiền {format_money(bill.amount)} VND"
                language = "vn"
                ipaddr = request.remote_addr

                vnp = vnpay()
                vnp.requestData["vnp_Version"] = "2.1.0"
                vnp.requestData["vnp_Command"] = "pay"
                vnp.requestData["vnp_TmnCode"] = current_app.config.get(
                    "VNPAY_TMN_CODE"
                )
                vnp.requestData["vnp_Amount"] = amount * 100
                vnp.requestData["vnp_CurrCode"] = "VND"
                vnp.requestData["vnp_TxnRef"] = order_id
                vnp.requestData["vnp_OrderInfo"] = order_desc
                vnp.requestData["vnp_OrderType"] = order_type
                vnp.requestData["vnp_Locale"] = language
                vnp.requestData["vnp_CreateDate"] = datetime.now().strftime(
                    "%Y%m%d%H%M%S"
                )
                vnp.requestData["vnp_IpAddr"] = ipaddr
                vnp.requestData["vnp_ReturnUrl"] = url_for(
                    "return-payment.index", mid=medical_registration_id, _external=True
                )
                vnpay_payment_url = vnp.get_payment_url(
                    current_app.config.get("VNPAY_PAYMENT_URL"),
                    current_app.config.get("VNPAY_HASH_SECRET_KEY"),
                )
                return redirect(vnpay_payment_url)
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


class ReturnPaymentView(CashierView):
    def is_visible(self):
        return False

    @expose("/", methods=["GET"])
    def index(self):
        inputData = request.args
        if inputData:
            vnp = vnpay()
            vnp.responseData = inputData.to_dict()
            order_id = inputData["vnp_TxnRef"]
            vnp_ResponseCode = inputData["vnp_ResponseCode"]
            bill = Bill.query.get(order_id)
            if bill and vnp.validate_response(
                current_app.config.get("VNPAY_HASH_SECRET_KEY")
            ):
                if vnp_ResponseCode == "00":
                    bill.fulfilled = True
                    bill.medical_examination.medical_registration.status = (
                        MedicalRegistrationStatus.COMPLETED
                    )
                    db.session.commit()
                    flash("Thanh toán hóa đơn thành công.", category="success")
                    return redirect(
                        url_for(
                            "pay-bill.index",
                            mid=bill.medical_examination.medical_registration.id,
                        )
                    )
            flash("Có lỗi xảy ra. Vui lòng thử lại.", category="danger")
            return redirect(url_for("pay-bill.index", mid=request.args.get("mid")))
        flash("Có lỗi xảy ra. Vui lòng thử lại.", category="danger")
        return redirect(url_for("pay-bill.index", mid=request.args.get("mid")))


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
        policy = Policy.query.filter(Policy.type == PolicyType.EXAMINATION_FEE).first()
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
        menu_icon_value="fa-book-medical",
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
    ReturnPaymentView(
        name="Kết quả thanh toán",
        menu_icon_type="fa",
        menu_icon_value="fa-users",
        endpoint="return-payment",
    )
)
dashboard.add_view(
    BillView(
        name="Tra cứu hoá đơn",
        menu_icon_type="fa",
        menu_icon_value=" fa-magnifying-glass",
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
