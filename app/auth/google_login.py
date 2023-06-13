import logging
from fastapi import APIRouter, status, Request
from pydantic import BaseModel
from starlette.responses import JSONResponse

from app.auth.login import LoginResponse
from app.settings.auth_settings import generate_token

router = APIRouter()
logger = logging.getLogger("app")


class GoogleLoginRequest(BaseModel):
    mail: str


@router.post("/google")
def login_google(request: Request, mail: GoogleLoginRequest):
    users = request.app.database["users"]
    user = users.find_one({"mail": mail.mail})
    if not user:
        return JSONResponse(status_code=status.HTTP_206_PARTIAL_CONTENT)

    if user["first_login"]:
        users.update_one({"mail": user.mail}, {"$set": {"first_login": False}})

    access_token = generate_token(str(user["_id"]), user["role"])

    request.app.logger.info(f"User logged in: {user.mail} | id: {user['_id']}")

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
