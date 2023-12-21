from flask import Blueprint

cashier = Blueprint("cashier", __name__)

from . import views
