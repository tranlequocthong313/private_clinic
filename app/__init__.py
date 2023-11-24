from dotenv import load_dotenv
from flask import Flask, render_template
from flask_migrate import Migrate

from app import admin
from app.config import Config
from app.controllers.index import blueprint as index_blueprint
from app.models import db

import cloudinary

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db, compare_type=True)

admin.init_admin(app, db)

cloudinary.config(
    cloud_name=app.get("CLOUDINARY_NAME"),
    api_key=app.get("CLOUDINARY_API_KEY"),
    api_secret=app.get("CLOUDINARY_API_SECRET"),
)

app.register_blueprint(index_blueprint)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
