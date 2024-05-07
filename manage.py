#!/usr/bin/env python3
from dotenv import load_dotenv

load_dotenv()


import os

import cloudinary

from app import create_app
from app.dashboard import *

app = create_app(config_name=os.getenv("FLASK_CONFIG") or "default")
print("app init")

cloudinary.config(
    cloud_name=app.get("CLOUDINARY_NAME"),
    api_key=app.get("CLOUDINARY_API_KEY"),
    api_secret=app.get("CLOUDINARY_API_SECRET"),
)
print("clouidnary init")

from app.dashboard import *

if __name__ == "__main__":
    print("importing stuff...")
    from app.models import create_default_data

    print("imported stuff")

    with app.app_context():
        print("create default data")
        create_default_data()
        print("created default data")

    app.run(port=10000, debug=app.config.get("ENVIRONMENT").lower() == "development")
