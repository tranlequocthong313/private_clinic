from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    IntegerField,
    TextAreaField,
    FieldList,
    FormField,
)
from wtforms.validators import DataRequired

from ..models import MedicineType, Medicine


class MedicineForm(FlaskForm):
    dosage = StringField("Cách dùng")
    quantity = IntegerField("Số lượng", default=1)
    unit = StringField("Đơn vị")
    delete_medicine = SubmitField("Xóa thuốc")


class MedicalExaminationForm(FlaskForm):
    name = StringField("Họ tên", validators=[DataRequired()])
    contact = StringField("Liên lạc", validators=[DataRequired()])
    diagnosis = TextAreaField("Chuẩn đoán", validators=[DataRequired()])
    symptom = StringField("Triệu chứng")

    medicines = FieldList(FormField(MedicineForm), min_entries=0)
    medicine_type = StringField("Nhóm thuốc", validators=[DataRequired()])
    medicine_name = StringField("Tên thuốc", validators=[DataRequired()])
    add_medicine = SubmitField("Thêm")

    submit = SubmitField("Tạo phiếu khám")

    def validate_medicine_type(self, field):
        if field.data not in MedicineType.query.all():
            field.errors.append("Loại thuốc không tồn tại.")

    def validate_medicine(self, field):
        if field.data not in Medicine.query.all():
            field.errors.append("Thuốc không tồn tại.")
