#!/usr/bin/env python3
from dotenv import load_dotenv

load_dotenv()


import os

import cloudinary

from app import create_app
from app.dashboard import *

app = create_app(config_name=os.getenv("FLASK_CONFIG") or "default")

cloudinary.config(
    cloud_name=app.get("CLOUDINARY_NAME"),
    api_key=app.get("CLOUDINARY_API_KEY"),
    api_secret=app.get("CLOUDINARY_API_SECRET"),
)

from app.dashboard import *

if __name__ == "__main__":
    from app.models import create_default_data

    with app.app_context():
        create_default_data()

    app.run(port=5555, debug=True)
