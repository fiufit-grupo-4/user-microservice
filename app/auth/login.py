import logging
import jwt
from os import environ
from bson import ObjectId
from dotenv import load_dotenv
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from starlette import status
from starlette.responses import JSONResponse
from fastapi import APIRouter, Request
from datetime import datetime, timedelta

load_dotenv()
JWT_SECRET = environ["JWT_SECRET"]
logger = logging.getLogger("app")
router = APIRouter()
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_token(_id: str, mail: str) -> str:
    utcnow = datetime.utcnow()
    expires = utcnow + timedelta(hours=1)
    token_data = {
        "_id": _id,
        "mail": mail,
        "exp": expires,
        "iat": utcnow,
    }
    token = jwt.encode(token_data, JWT_SECRET, algorithm="HS256")
    return token


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/", status_code=status.HTTP_200_OK)
def login(credentials: HTTPBasicCredentials, request: Request):
    users = request.app.database["users"]
    user = users.find_one({"mail": credentials.username})

    if not user or not verify_password(
        credentials.password, user['encrypted_password']
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Invalid credentials",
        )

    access_token = generate_token(str(user["_id"]), user["mail"])
    # users.update_one({"mail": credentials.username}, {"$set": {"session_token": session_token}})
    return {"access_token": access_token, "token_type": "bearer"}
