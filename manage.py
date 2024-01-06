#!/usr/bin/env python
from dotenv import load_dotenv

load_dotenv()

import os
from app import create_app, db
import cloudinary

app = create_app(config_name=os.getenv("FLASK_CONFIG") or "default")

cloudinary.config(
    cloud_name=app.get("CLOUDINARY_NAME"),
    api_key=app.get("CLOUDINARY_API_KEY"),
    api_secret=app.get("CLOUDINARY_API_SECRET"),
)

from app.dashboard import *

if __name__ == "__main__":
    app.run(port=5555)
