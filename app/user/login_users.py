from http.client import HTTPException
from fastapi import APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from starlette import status
from starlette.responses import JSONResponse

from app.domain.token_generator import UUIDTokenGenerator

router = APIRouter()

security = HTTPBasic()

token_generator = UUIDTokenGenerator()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_login = {
    "foo": {
        "username": "foo",
        "full_name": "Lucas",
        "email": "ss@gmail.com",
        "hashed_password": "pepe",
    }
}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str):
    if username in users_login:
        user_dict = users_login[username]
        return user_dict
    return None


@router.post("/", status_code=status.HTTP_200_OK)
def login(credentials: HTTPBasicCredentials):
    user = get_user(credentials.username)
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Invalid credentials",
        )
    user.create_session(token_generator)
    return {"sessionToken": user["session_token"]}
