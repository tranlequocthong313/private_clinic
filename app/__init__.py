from datetime import date
import os

from flask import Flask, render_template, make_response, Response, url_for
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap4
from twilio.rest import Client

from config import config
from .utils import format_money

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
bootstrap = Bootstrap4()
sms_client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))


def create_app(*args, **kwargs):
    app = Flask(__name__)
    app.config.from_object(config[kwargs.get("config_name", "default")])
    app.jinja_env.globals.update(format_money=format_money)

    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db, compare_type=True)

    if not os.path.exists(app.config.get("UPLOAD_FOLDER")):
        os.makedirs(app.config.get("UPLOAD_FOLDER"))

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from .api import api as api_blueprint

    app.register_blueprint(api_blueprint, url_prefix="/api")

    def has_no_empty_params(rule):
        defaults = rule.defaults if rule.defaults is not None else ()
        arguments = rule.arguments if rule.arguments is not None else ()
        return len(defaults) >= len(arguments)

    @app.route("/site-map")
    def site_map():
        links = []
        for rule in app.url_map.iter_rules():
            # Filter out rules we can't navigate to in a browser
            # and rules that require parameters
            if "GET" in rule.methods and has_no_empty_params(rule):
                url = url_for(rule.endpoint, **(rule.defaults or {}))
                links.append((url, rule.endpoint))
        # links is now a list of url, endpoint tuples

        return links

    return app
