from dotenv import load_dotenv
from fastapi import APIRouter, Request, status
from starlette.responses import JSONResponse

from app.auth.login import LoginResponse
from app.auth.signup import signup
from app.settings.auth_settings import generate_token
from app.user.user import UserSignUpCredentials, UserResponse
from app.definitions import GOOGLE_SIGNUP


load_dotenv()
router = APIRouter()


@router.post("/google", status_code=status.HTTP_201_CREATED)
def signup_with_google(credentials: UserSignUpCredentials, request: Request):
    users = request.app.database["users"]

    if users.find_one({"mail": credentials.mail}, {"_id": 0}):
        msg_user_exist = f"User {credentials.mail} already exists"
        request.app.logger.info(msg_user_exist)

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content=msg_user_exist
        )

    signup(credentials, request)

    user = users.find_one({"mail": credentials.mail})

    user_id = str(user["_id"])
    access_token = generate_token(user_id, user["role"])

    request.state.metrics_allowed = True
    request.state.user_id = user_id
    request.state.action = GOOGLE_SIGNUP

    return LoginResponse(
        id=user["_id"],
        mail=user["mail"],
        role=user["role"],
        phone_number=user["phone_number"],
        name=user["name"],
        lastname=user["lastname"],
        age=user["age"],
        blocked=user["blocked"],
        image=user["image"],
        location=user["location"],
        access_token=access_token,
        token_type="bearer",
        first_login=user["first_login"],
    )
