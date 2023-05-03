import jwt
from os import environ
from passlib.context import CryptContext
from pydantic import BaseSettings
from datetime import timedelta, datetime

JWT_SECRET = environ.get("JWT_SECRET", "mysecretkey")
JWT_ALGORITHM = environ.get("JWT_ALGORITHM", "HS256")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
RESET_PASSWORD_EXPIRATION_MINUTES = environ.get("RESET_PASSWORD_EXPIRATION_MINUTES", 60)
EXPIRES = timedelta(minutes=int(RESET_PASSWORD_EXPIRATION_MINUTES))


def generate_token(id: str) -> str:
    utcnow = datetime.utcnow()
    expires = utcnow + timedelta(hours=1)
    token_data = {
        "id": id,
        "exp": expires,
        "iat": utcnow,
    }
    token = jwt.encode(token_data, JWT_SECRET, algorithm="HS256")
    return token


class Settings(BaseSettings):
    def generate_token(id: str) -> str:
        utcnow = datetime.utcnow()
        expires = utcnow + EXPIRES
        token_data = {
            "id": id,
            "exp": expires,
            "iat": utcnow,
        }
        token = jwt.encode(token_data, key=JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
