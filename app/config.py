import os
from urllib.parse import quote


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    db_host = os.getenv("DATABASE_HOST")
    db_name = os.getenv("DATABASE_NAME")
    db_port = os.getenv("DATABASE_PORT")
    db_username = os.getenv("DATABASE_USERNAME")
    db_password = os.getenv("DATABASE_PASSWORD")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{quote(db_username)}:{quote(db_password)}"
    )
    SQLALCHEMY_DATABASE_URI += (
        f"@{quote(db_host)}:{quote(db_port)}/{quote(db_name)}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = True
