from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse
from twilio.rest import Client

from app.settings.config import pwd_context, account_sid, auth_token
from app.settings.twilio import send_whatsapp_validation_code, twilio_validation_code
from app.user.user import User, UserBasicCredentials, UserResponse

router = APIRouter()
client_twilio = Client(account_sid, auth_token)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(credentials: UserBasicCredentials, request: Request):
    hashed_password = pwd_context.hash(credentials.password)
    user = User(
        credentials.mail,
        hashed_password,
        role=credentials.role,
        phone_number=credentials.phone_number,
    )

    users = request.app.database["users"]

    if users.find_one({"mail": credentials.mail}, {"_id": 0}):
        request.app.logger.info(f"User {credentials.mail} already exists")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=f'User {credentials.mail} already exists',
        )
    user_id = users.insert_one(jsonable_encoder(user)).inserted_id

    request.app.logger.info(
        f"User {UserResponse(id=str(user_id), mail=user.mail, phone_number=user.phone_number)} successfully created"
    )

    send_whatsapp_validation_code(credentials.phone_number)

    return UserResponse(id=str(user_id), mail=user.mail, phone_number=user.phone_number)


@router.post("/validate_verification_code")
async def validate_verification_code(
    phone_number: str, verification_code: str, request: Request
):
    await twilio_validation_code(phone_number, verification_code)
    return {"detail": "Sign up successfully"}
