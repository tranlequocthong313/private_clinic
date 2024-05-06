from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class SearchingPatientForm(FlaskForm):
    keyword = StringField("Tìm kiếm", render_kw={"placeholder": "Từ khóa"})
    submit = SubmitField("Tra cuu")
