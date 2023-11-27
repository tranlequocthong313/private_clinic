from flask import Blueprint

nurse = Blueprint("nurse", __name__)

from . import views
