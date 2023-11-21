from dotenv import load_dotenv

load_dotenv()

from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.config import Config
from app.controllers.index import blueprint as index_blueprint


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)

app.register_blueprint(index_blueprint)
from app import admin

if __name__ == '__main__':
    app.run(debug=True)

