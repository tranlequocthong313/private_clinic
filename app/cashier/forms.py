from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField, RadioField
from wtforms.validators import DataRequired


class PayBillForm(FlaskForm):
    name = StringField("Họ tên")
    contact = StringField("Liên lạc")
    examination_fee = StringField("Tiền khám")
    medicine_fee = StringField("Tiền thuốc")
    sum_fee = StringField("Tổng tiền")
    pay_options = RadioField(
        "Hình thức thanh toán",
        choices=[
            ("cash", "Thanh toán bằng tiền mặt"),
            ("vnpay", "Thanh toán qua VNPAY"),
        ],
        default="cash",
    )
    submit = SubmitField("Thanh toán")


class SearchBillForm(FlaskForm):
    id = StringField("Mã hóa đơn")
    submit = SubmitField("Tìm kiếm")
