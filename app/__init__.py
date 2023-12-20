import os

from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap4
from twilio.rest import Client
from flask_admin import Admin

from config import config

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
bootstrap = Bootstrap4()
sms_client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))


def create_app(*args, **kwargs):
    app = Flask(__name__)
    app.config.from_object(config[kwargs.get("config_name", "default")])

    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db, compare_type=True)

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .doctor import doctor as doctor_blueprint

    app.register_blueprint(doctor_blueprint, url_prefix="/dashboard")

    from .patient import patient as patient_blueprint

    app.register_blueprint(patient_blueprint, url_prefix="/dashboard")

    from .nurse import nurse as nurse_blueprint

    app.register_blueprint(nurse_blueprint, url_prefix="/dashboard")

    from .medicine import medicine as medicine_blueprint

    app.register_blueprint(medicine_blueprint, url_prefix="/dashboard")

    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from .api import api as api_blueprint

    app.register_blueprint(api_blueprint, url_prefix="/api")

    return app
