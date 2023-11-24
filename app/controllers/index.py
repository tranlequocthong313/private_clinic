from flask import Blueprint, render_template

from app.models import User


blueprint = Blueprint("index", __name__)


@blueprint.route("/")
@blueprint.route("/home")
def home():
    return render_template("landing_page.html")


@blueprint.route("/contact")
def contact():
    return render_template("contact.html")


@blueprint.route("/about")
def about():
    return render_template("about.html")


@blueprint.route("/login")
def login():
    return "<h1>Login</h1>"
