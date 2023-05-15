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
        msg_user_exist = f"User {credentials.mail} already exists"
        request.app.logger.info(msg_user_exist)
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content=msg_user_exist
        )
    user_id = users.insert_one(jsonable_encoder(user)).inserted_id
    response = UserResponse(
        id=str(user_id), mail=user.mail, phone_number=user.phone_number, name=user.name
    )

    request.app.logger.info(f"User {response} successfully created")

    send_whatsapp_validation_code(credentials.phone_number)

    return response


@router.post("/validate_code")
async def validate_verification_code(
    phone_number: str, verification_code: str, request: Request
):
    await twilio_validation_code(phone_number, verification_code)
    return {"detail": "Sign up successfully"}
