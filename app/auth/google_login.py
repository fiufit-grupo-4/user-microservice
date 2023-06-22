import logging
from fastapi import APIRouter, status, Request
from pydantic import BaseModel, EmailStr, Field
from starlette.responses import JSONResponse

from app.auth.login import LoginResponse, is_role_valid
from app.settings.auth_settings import generate_token
from app.definitions import GOOGLE_LOGIN

router = APIRouter()
logger = logging.getLogger("app")


class GoogleLoginRequest(BaseModel):
    mail: EmailStr = Field(example="username@mail.com")


@router.post("/google")
def login_google(request: Request, credentials: GoogleLoginRequest):
    users = request.app.database["users"]
    user = users.find_one({"mail": credentials.mail})
    if not user:
        return JSONResponse(status_code=status.HTTP_206_PARTIAL_CONTENT)

    if user["blocked"]:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED)

    logger.info(f"User logged in: {user}")

    if user["first_login"]:
        users.update_one({"mail": credentials.mail}, {"$set": {"first_login": False}})

    user_id = str(user["_id"])

    access_token = generate_token(user_id, user["role"])

    request.state.metrics_allowed = True
    request.state.user_id = user_id
    request.state.action = GOOGLE_LOGIN

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
        user["first_login"],
    )
