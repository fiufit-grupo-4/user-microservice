from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBasicCredentials
from passlib.context import CryptContext
from starlette import status
from starlette.responses import JSONResponse

from app.user.user import User

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/", status_code=status.HTTP_200_OK)
def signup(credentials: HTTPBasicCredentials, request: Request):
    hashed_password = pwd_context.hash(credentials.password)
    user = User(credentials.username, hashed_password)

    users = request.app.database["users"]

    if users.find_one({"mail": credentials.username}, {"_id": 0}):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=f'User {credentials.username} already exists'
        )

    users.insert_one(jsonable_encoder(user))
    return user
