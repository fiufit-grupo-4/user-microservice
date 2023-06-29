from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse
from twilio.rest import Client

from app.domain.UserRoles import UserRoles
from app.config.config import Settings, pwd_context
from app.config.twilio import send_whatsapp_validation_code, twilio_validation_code
from app.user.user import User, UserSignUpCredentials, UserResponse
from app.definitions import SIGNUP

router = APIRouter()
app_settings = Settings()
client_twilio = Client(app_settings.TWILIO_ACCOUNT_SID, app_settings.TWILIO_AUTH_TOKEN)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(credentials: UserSignUpCredentials, request: Request):
    hashed_password = pwd_context.hash(credentials.password)
    user = User(
        credentials.mail,
        hashed_password,
        role=credentials.role,
        phone_number=credentials.phone_number,
        name=credentials.name,
        lastname=credentials.lastname,
        age=credentials.age,
        location=credentials.location,
        image=credentials.image,
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
        id=str(user_id),
        mail=user.mail,
        role=user.role,
        phone_number=user.phone_number,
        name=user.name,
        lastname=user.lastname,
        age=user.age,
        blocked=user.blocked,
        image=user.image,
        trainings=user.trainings,
        location=user.location,
    )

    request.app.logger.info(f"User {response} successfully created")
    if user.role != UserRoles.ADMIN.value:
        send_whatsapp_validation_code(credentials.phone_number)

    request.state.metrics_allowed = True
    request.state.location = user.location
    request.state.user_id = user_id
    request.state.action = SIGNUP
    return response


@router.post("/validate_code")
async def validate_verification_code(
    phone_number: str, verification_code: str, request: Request
):
    return await twilio_validation_code(phone_number, verification_code)
