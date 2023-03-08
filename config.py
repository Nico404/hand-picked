import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Database
    SECRET_KEY = "SECRET_KEY"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        basedir, "backend/handpicked.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # email service
    with open(os.path.join(basedir, "secret/mailgun_apikey.txt"), "r") as apikey:
        MAILGUN_API_KEY = apikey.read()
    MAILGUN_DOMAIN = "your_mailgun_domain"
