import jwt

from http.client import HTTPException
from passlib.context import CryptContext
from bson import ObjectId
from fastapi import Depends
from pydantic import BaseSettings
from datetime import datetime, timedelta
from starlette import status
from app.config.auth_baerer import JWTBearer
from app.config.config import Settings, pwd_context

app_settings = Settings()


def get_user_id(token: str = Depends(JWTBearer())) -> ObjectId:
    try:
        token_data_user = jwt.decode(
            token, app_settings.JWT_SECRET, algorithms=app_settings.JWT_ALGORITHM
        )
        return ObjectId(token_data_user["id"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )


def generate_token(id: str, role) -> str:
    utcnow = datetime.utcnow()
    expires = utcnow + timedelta(hours=1)
    token_data = {"id": id, "exp": expires, "iat": utcnow, "role": role}
    token = jwt.encode(
        token_data, app_settings.JWT_SECRET, algorithm=app_settings.JWT_ALGORITHM
    )
    return token


class SettingsAuth(BaseSettings):
    def generate_token(id: str) -> str:
        utcnow = datetime.utcnow()
        expires = utcnow + app_settings.EXPIRES
        token_data = {
            "id": id,
            "exp": expires,
            "iat": utcnow,
        }
        token = jwt.encode(
            token_data,
            key=app_settings.JWT_SECRET,
            algorithm=app_settings.JWT_ALGORITHM,
        )
        return token

    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
