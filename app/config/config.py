from dotenv import load_dotenv
from logging.config import dictConfig
from os import environ
from pydantic import BaseSettings
from app.config.log_config import logconfig
from datetime import timedelta
from passlib.context import CryptContext
import logging

load_dotenv()
dictConfig(logconfig)
logger = logging.getLogger('app')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Settings(BaseSettings):
    PORT: int = environ.get("PORT", 7501)
    DB_PORT: int = environ.get("DB_PORT", 27017)
    MONGODB_URI: str = environ.get("MONGODB_URI", "mongodb:27017")
    JWT_SECRET: str = environ.get("JWT_SECRET", "123456")
    JWT_ALGORITHM: str = environ.get("JWT_ALGORITHM", "HS256")
    RESET_PASSWORD_EXPIRATION_MINUTES = environ.get(
        "RESET_PASSWORD_EXPIRATION_MINUTES", 60
    )
    EXPIRES = timedelta(minutes=int(RESET_PASSWORD_EXPIRATION_MINUTES))
    USER_SERVICE_URL: str = environ.get(
        'USER_SERVICE_URL', 'http://user-microservice:7500'
    )
    TRAINING_SERVICE_URL = environ.get(
        'TRAINING_SERVICE_URL', 'http://training-microservice:7501'
    )
    GOALS_SERVICE_URL: str = environ.get(
        "GOALS_SERVICE_URL", "http://goals-microservice:7502"
    )
    TZ: str = environ.get("TZ", "America/Argentina/Buenos_Aires")
    CLOUDAMQP_URL: str = environ.get("CLOUDAMQP_URL", "todo-me")
    SENGRID_EMAIL_TEMPLATE_ID: str = environ.get('SENGRID_EMAIL_TEMPLATE_ID', 'todo-me')
    TWILIO_ACCOUNT_SID: str = environ.get('TWILIO_ACCOUNT_SID', 'todo-me')
    TWILIO_AUTH_TOKEN = environ.get('TWILIO_AUTH_TOKEN', 'todo-me')
    TWILIO_SERVICES = environ.get('TWILIO_SERVICES', 'todo-me')
    FIREBASE_PROJECT_ID: str = str(environ.get("FIREBASE_PROJECT_ID", 'todo-me'))
    FIREBASE_PRIVATE_KEY_ID: str = str(environ.get("FIREBASE_PRIVATE_KEY_ID", 'todo-me'))
    FIREBASE_PRIVATE_KEY: str = str(environ.get("FIREBASE_PRIVATE_KEY", 'todo-me')).replace(
        '\\n', '\n'
    )
    FIREBASE_CLIENT_EMAIL: str = str(environ.get("FIREBASE_CLIENT_EMAIL", 'todo-me'))
    FIREBASE_CLIENT_ID: str = str(environ.get("FIREBASE_CLIENT_ID", 'todo-me'))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
