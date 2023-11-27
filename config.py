import os
from urllib.parse import quote


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SALT = os.getenv("SALT")
    ITEMS_PER_PAGE = os.getenv("ITEMS_PER_PAGE")


class DevelopmentConfig(Config):
    DEBUG = True

    db_host = os.getenv("DATABASE_HOST")
    db_name = os.getenv("DATABASE_NAME")
    db_port = os.getenv("DATABASE_PORT")
    db_username = os.getenv("DATABASE_USERNAME")
    db_password = os.getenv("DATABASE_PASSWORD")

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{quote(db_username)}:{quote(db_password)}@{quote(db_host)}:{quote(db_port)}/{quote(db_name)}?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    CLOUDINARY_NAME = os.getenv("CLOUDINARY_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_SUBJECT_PREFIX = "[Phòng khám]"
    MAIL_SENDER = f"Hệ thống <{os.getenv('MAIL_SENDER')}>"
    ADMIN = os.getenv("ADMIN")


config = {"development": DevelopmentConfig, "default": DevelopmentConfig}
