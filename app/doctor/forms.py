from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    IntegerField,
    TextAreaField,
    FieldList,
    FormField,
    HiddenField,
)
from wtforms.validators import DataRequired

from ..models import MedicineType, Medicine


class MedicineForm(FlaskForm):
    medicine_id = HiddenField()
    medicine_name = StringField("Thuốc")
    dosage = StringField("Cách dùng")
    quantity = IntegerField("Số lượng", default=1)
    unit = StringField("Đơn vị")
    delete_medicine = SubmitField("Xóa thuốc")


class MedicalExaminationForm(FlaskForm):
    name = StringField("Họ tên", validators=[DataRequired()])
    contact = StringField("Liên lạc", validators=[DataRequired()])
    diagnosis = TextAreaField("Chẩn đoán")
    advice = TextAreaField("Lời dặn")
    symptom = StringField("Triệu chứng")

    medicines = FieldList(FormField(MedicineForm), min_entries=0)
    medicine_type = StringField("Nhóm thuốc")
    medicine_name = StringField("Tên thuốc")
    add_medicine = SubmitField("Thêm")

    draft = SubmitField("Lưu nháp")
    submit = SubmitField("Tạo phiếu khám")

    def validate_medicine_type(self, field):
        if field.data not in [mt.name for mt in MedicineType.query.all()]:
            field.errors.append("Loại thuốc không tồn tại.")

    def validate_medicine(self, field):
        if field.data not in [m.name for m in Medicine.query.all()]:
            field.errors.append("Thuốc không tồn tại.")

    def validate(self, extra_validators=None):
        if super().validate(extra_validators):
            if self.add_medicine.data:
                if not self.medicine_name:
                    self.medicine_name.errors.append("Thuốc không được bỏ trống.")
                    return False
            elif self.draft.data:
                if not (self.diagnosis.data or self.medicines.data):
                    return False
            elif self.submit.data:
                if not self.diagnosis.data:
                    self.diagnosis.errors.append("Chưa đưa ra chẩn đoán cho bệnh nhân.")
                    return False
        return True
