import logging

from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.settings.config import pwd_context
from app.user.user import UserLoginCredentials
from app.settings.auth_settings import generate_token
from app.auth.password_reset import router as password_router
from app.auth.google_login import router as google_login_router
from app.definitions import LOGIN

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
        id,
        mail,
        phone_number,
        role,
        name,
        lastname,
        age,
        image,
        blocked,
        location,
        access_token,
        token_type,
    ):
        self.id = str(id)
        self.name = name
        self.lastname = lastname
        self.age = age
        self.mail = mail
        self.role = role
        self.image = image
        self.blocked = blocked
        self.phone_number = phone_number
        self.location = location
        self.access_token = access_token
        self.token_type = token_type


def is_password_valid(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def is_role_valid(credentials_role, user_role):
    return credentials_role >= user_role


@router.post("/", status_code=status.HTTP_200_OK)
def login(credentials: UserLoginCredentials, request: Request):

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

    request.state.metrics_allowed = True
    request.state.user_id = user['_id']
    request.state.action = LOGIN

    return LoginResponse(
        user["_id"],
        user["mail"],
        user["phone_number"],
        user["role"],
        user["name"],
        user["lastname"],
        user["age"],
        user["image"],
        user["blocked"],
        user["location"],
        access_token,
        "bearer",
    )
