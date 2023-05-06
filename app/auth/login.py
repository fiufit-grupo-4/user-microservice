import logging
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.domain import UserRoles
from app.user.user import UserBasicCredentials
from app.settings.auth_settings import Settings, pwd_context, generate_token
from app.auth.password_reset import router as password_router

load_dotenv()
logger = logging.getLogger("app")
router = APIRouter()
setting = Settings()

router.include_router(password_router, tags=["login"], prefix="")


def is_password_valid(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def is_role_valid(credentials_role, user_role):
    return credentials_role >= user_role


@router.post("/", status_code=status.HTTP_200_OK)
def login(credentials: UserBasicCredentials, request: Request):
    users = request.app.database["users"]
    user = users.find_one({"mail": credentials.mail})

    if not user or not is_password_valid(credentials.password, user['encrypted_password']) \
            or not is_role_valid(credentials.role, user["role"]):
        request.app.logger.info(f"User failed to login: {credentials.mail}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Invalid credentials",
        )

    access_token = generate_token(str(user["_id"]))

    request.app.logger.info(f"User logged in: {credentials.mail} | id: {user['_id']}")
    return {"access_token": access_token, "token_type": "bearer"}
