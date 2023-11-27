from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField
from wtforms.validators import DataRequired, Email


class SearchingMedicineForm(FlaskForm):
    id = StringField("Ma thuoc")
    name = StringField("Ten thuoc")
    submit = SubmitField("Tra cuu")
