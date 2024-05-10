import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # base configuration

    # FLASK
    SECRET_KEY = os.getenv("SECRET_KEY")
    REMEMBER_COOKIE_SAMESITE = os.getenv("REMEMBER_COOKIE_SAMESITE")
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE")
    DEBUG = os.getenv("DEBUG")
    SERVER_NAME = os.getenv("SERVER_NAME")

    # FLASK-SQLALCHEMY
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")  # set the database URI

    # FLASK SECURITY TOO
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")
    SECURITY_RECOVERABLE = os.getenv("SECURITY_RECOVERABLE")
    SECURITY_CHANGEABLE = os.getenv("SECURITY_CHANGEABLE")
    SECURITY_REGISTERABLE = os.getenv("SECURITY_REGISTERABLE")
    SECURITY_TRACKABLE = os.getenv("SECURITY_TRACKABLE")
    SECURITY_USERNAME_ENABLE = os.getenv("SECURITY_USERNAME_ENABLE")
    SECURITY_USERNAME_REQUIRED = os.getenv("SECURITY_USERNAME_REQUIRED")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    SECURITY_EMAIL_SUBJECT_PASSWORD_RESET = os.getenv("SECURITY_EMAIL_SUBJECT_PASSWORD_RESET")
    SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE = os.getenv("SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE")
    SECURITY_EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE = os.getenv("SECURITY_EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE")