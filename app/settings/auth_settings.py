from http.client import HTTPException
import jwt
from bson import ObjectId
from fastapi import Depends
from pydantic import BaseSettings
from datetime import datetime
from starlette import status
from app.settings.auth_baerer import JWTBearer
from app.settings.config import *


def get_user_id(token: str = Depends(JWTBearer())) -> ObjectId:
    try:
        token_data_user = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return ObjectId(token_data_user["id"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )


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
