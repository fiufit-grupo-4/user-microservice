from dotenv import load_dotenv
from fastapi import APIRouter, Request, status

from app.auth.login import LoginResponse
from app.auth.signup import signup
from app.settings.auth_settings import generate_token
from app.user.user import UserSignUpCredentials

load_dotenv()
router = APIRouter()


@router.post("/google", status_code=status.HTTP_201_CREATED)
def signup_with_google(credentials: UserSignUpCredentials, request: Request):
    signup(credentials, request)

    users = request.app.database["users"]
    user = users.find_one({"mail": credentials.mail})

    access_token = generate_token(str(user["_id"]), user["role"])

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
