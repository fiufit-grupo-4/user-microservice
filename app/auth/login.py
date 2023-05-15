import logging
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from app.domain.UserRoles import UserRoles
from app.settings.config import pwd_context
from app.user.training_small import TrainingResponse
from app.user.user import UserBasicCredentials
from app.settings.auth_settings import generate_token
from app.auth.password_reset import router as password_router
from app.auth.google_login import router as google_login_router
from app.user.utils import ObjectIdPydantic

load_dotenv()
logger = logging.getLogger("app")
router = APIRouter()

router.include_router(password_router, tags=["login"], prefix="")
router.include_router(
    google_login_router,
    prefix="",
    tags=["login"],
)


class LoginResponse:
    def __init__(
        self,
        mail,
        phone_number,
        role,
        name,
        lastname,
        age,
        image,
        blocked,
        trainings,
        access_token,
        token_type
    ):
        self.name = name
        self.lastname = lastname
        self.age = age
        self.mail = mail
        self.role = role
        self.image = image
        self.blocked = blocked
        self.phone_number = phone_number
        self.trainings = trainings
        self.access_token = access_token
        self.token_type = token_type


def is_password_valid(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def is_role_valid(credentials_role, user_role):
    return credentials_role >= user_role


@router.post("/", status_code=status.HTTP_200_OK)
def login(credentials: UserBasicCredentials, request: Request):
    users = request.app.database["users"]
    user = users.find_one({"mail": credentials.mail})

    if (
        not user
        or not is_password_valid(credentials.password, user['encrypted_password'])
        or not is_role_valid(credentials.role, user["role"])
    ):
        request.app.logger.info(f"User failed to login: {credentials.mail}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Invalid credentials",
        )

    access_token = generate_token(str(user["_id"]), user["role"])

    request.app.logger.info(f"User logged in: {credentials.mail} | id: {user['_id']}")

    return LoginResponse(user["mail"], user["phone_number"], user["role"], user["name"], user["lastname"], user["age"], user["image"],
                         user["blocked"], user["trainings"], access_token, "bearer")
