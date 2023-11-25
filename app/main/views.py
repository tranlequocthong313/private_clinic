from flask import render_template
from flask_login import login_required

from . import main
from .forms import MedicalRegisterForm
from ..decorators import confirmed_required


@main.route("/")
def index():
    return render_template("landing_page.html")


@main.route("/contact")
def contact():
    return render_template("contact.html")


@main.route("/about")
def about():
    return render_template("about.html")


@main.route("/medical-register", methods=["GET", "POST"])
@login_required
@confirmed_required
def medical_register():
    form = MedicalRegisterForm()
    if form.validate_on_submit():
        # Thuc hien tao phieu dang ky kham va cac logic khac
        pass
    return render_template("medical_register.html", form=form)
