from flask import Blueprint

medicine = Blueprint("medicine", __name__)

from . import views
