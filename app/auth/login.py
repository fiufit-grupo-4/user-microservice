from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from starlette import status
from starlette.responses import JSONResponse
from fastapi import APIRouter, Request

from app.domain.token_generator import UUIDTokenGenerator

router = APIRouter()

security = HTTPBasic()

token_generator = UUIDTokenGenerator()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/", status_code=status.HTTP_200_OK)
def login(credentials: HTTPBasicCredentials, request: Request):
    users = request.app.database["users"]
    user = users.find_one({"mail": credentials.username}, {"_id": 0})

    if not user or not verify_password(credentials.password, user['encrypted_password']):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Invalid credentials",
        )

    session_token = token_generator.generate_session_token()
    #users.update_one({"mail": credentials.username}, {"$set": {"session_token": session_token}})
    return {"sessionToken": session_token}
