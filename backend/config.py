import os
from datetime import timedelta
from urllib.parse import quote_plus
from dotenv import load_dotenv

BASE = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE, ".env"))


def _b(k, d="false"):
    return os.getenv(k, d).lower() == "true"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-jwt-secret-at-least-32-characters")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    USE_SQLITE = _b("USE_SQLITE")
    MYSQL = dict(host=os.getenv("MYSQL_HOST", "localhost"), port=int(os.getenv("MYSQL_PORT", "3306")),
                 user=os.getenv("MYSQL_USER", "root"), password=os.getenv("MYSQL_PASSWORD", ""),
                 db=os.getenv("MYSQL_DATABASE", "talentiq_db"))
    SQLALCHEMY_DATABASE_URI = ("sqlite:///" + os.path.join(BASE, "talentiq.db")) if USE_SQLITE else \
        "mysql+pymysql://{user}:{pw}@{host}:{port}/{db}".format(
            user=MYSQL["user"], pw=quote_plus(MYSQL["password"]), host=MYSQL["host"], port=MYSQL["port"], db=MYSQL["db"])
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 40 * 1024 * 1024
    UPLOAD_DIR = os.path.join(BASE, "uploads")
    CHROMA_DIR = os.path.join(BASE, "chroma_data")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587") or 587)
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
