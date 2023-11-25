from flask import Blueprint, render_template

blueprint = Blueprint("index", __name__)


@blueprint.route("/")
@blueprint.route("/home")
def home():
    return render_template("landing_page.html")


@blueprint.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@blueprint.route("/contact")
def contact():
    return render_template("contact.html")


@blueprint.route("/about")
def about():
    return render_template("about.html")


@blueprint.route("/doctor")
def doctor():
    return render_template("doctor.html")


@blueprint.route("/login")
def login():
    return render_template("login.html")


@blueprint.route("/register")
def register():
    return render_template("register.html")
