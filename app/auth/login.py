import logging
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.user.user import UserBasicCredentials
from app.settings.auth_settings import Settings, pwd_context, generate_token
from app.auth.password_reset import router as password_router
from app.auth.google_login import router as google_login_router

load_dotenv()
logger = logging.getLogger("app")
router = APIRouter()
setting = Settings()

router.include_router(password_router, tags=["login"], prefix="")

router.include_router(
    google_login_router,
    prefix="",
    tags=["login"],
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/", status_code=status.HTTP_200_OK)
def login(credentials: UserBasicCredentials, request: Request):
    users = request.app.database["users"]
    user = users.find_one({"mail": credentials.mail})

    if not user or not verify_password(
        credentials.password, user['encrypted_password']
    ):
        request.app.logger.info(f"User failed to login: {credentials.mail}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Invalid credentials",
        )

    access_token = generate_token(str(user["_id"]))

    request.app.logger.info(f"User logged in: {credentials.mail} | id: {user['_id']}")
    return {"access_token": access_token, "token_type": "bearer"}
