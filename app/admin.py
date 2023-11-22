from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app.models import (
    AppointmentSchedule,
    Bill,
    MedicalExamination,
    MedicalRegistration,
    Medicine,
    MedicineType,
    MedicineUnit,
    Policy,
    User,
)


class CustomModelView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    can_export = True
    can_view_details = True


class MedicineView(CustomModelView):
    column_list = ["id", "name", "medicine_unit"]


def init_admin(app, db):
    admin = Admin(app, name="Admin", template_mode="bootstrap4")
    admin.add_view(CustomModelView(User, db.session))
    admin.add_view(CustomModelView(Policy, db.session))
    admin.add_view(MedicineView(Medicine, db.session))
    admin.add_view(CustomModelView(MedicineUnit, db.session))
    admin.add_view(CustomModelView(MedicineType, db.session))
    admin.add_view(CustomModelView(MedicalExamination, db.session))
    admin.add_view(CustomModelView(MedicalRegistration, db.session))
    admin.add_view(CustomModelView(Bill, db.session))
    admin.add_view(CustomModelView(AppointmentSchedule, db.session))
