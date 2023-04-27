import logging
import os

from dotenv import load_dotenv
from fastapi import APIRouter
from datetime import datetime
from datetime import timedelta
import jwt
from fastapi import Request, status
from fastapi.responses import JSONResponse
from passlib.handlers.bcrypt import bcrypt
from starlette.background import BackgroundTasks
from app.user.user import UserBasicCredentials
from app.settings.auth_settings import Settings, JWT_SECRET, JWT_ALGORITHM, pwd_context
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from sendgrid.helpers.mail import Mail

load_dotenv()
logger = logging.getLogger("app")
router = APIRouter()
setting = Settings()

def generate_token(id: str) -> str:
    utcnow = datetime.utcnow()
    expires = utcnow + timedelta(hours=1)
    token_data = {
        "id": id,
        "exp": expires,
        "iat": utcnow,
    }
    token = jwt.encode(token_data, JWT_SECRET, algorithm="HS256")
    return token

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

@router.post("/forgot_password", status_code=status.HTTP_200_OK)
async def forgot_password(credentials: UserBasicCredentials, background_tasks: BackgroundTasks, request: Request):
    users = request.app.database["users"]
    user = users.find_one({"mail": credentials.mail})

    if not user:
        request.app.logger.info(f"User not found: {credentials.mail}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="User not found",
        )

    reset_password_token = generate_token(str(user["_id"]))

    reset_password_url = f"{request.url.scheme}://{request.url.hostname}/reset_password?token={reset_password_token}"

    background_tasks.add_task(
        send_password_reset_email, to_email=user["mail"], reset_password_url=reset_password_url
    )

    request.app.logger.info(f"Password reset link sent to: {user['mail']}")
    return {"detail": "Password reset link sent"}




def send_password_reset_email(to_email, reset_password_url):

    message = Mail(
        from_email='waistenlucas@gmail.com',
        to_emails=to_email,
        subject='Reset your password',
        html_content=f'Click <a href="{reset_password_url}">here</a> to reset your password'
    )

    try:
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        client = Client(account_sid, auth_token)

        verification = client.verify \
            .v2 \
            .services('VA7d2f71f16e48ee0cb7e08d3af9358c3f') \
            .verifications \
            .create(channel_configuration={
            'template_id': 'd-dff889c4a40d4b48b7be17edaf1ec577',
            'from': 'lwaisten@fi.uba.ar',
            'from_name': 'Lucas Waisten'
        }, to=to_email, channel='email')

        print(verification.sid)
    except TwilioRestException as e:
        print(e)
    except Exception as e:
        print(e)

@router.post("/reset_password", status_code=status.HTTP_200_OK)
async def reset_password(credentials: UserBasicCredentials, token: str, request: Request):
    try:
        token_data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.exceptions.ExpiredSignatureError:
        request.app.logger.info(f"Password reset token expired: {token}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Password reset token expired",
        )
    except jwt.exceptions.InvalidTokenError:
        request.app.logger.info(f"Invalid password reset token: {token}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Invalid password reset token",
        )

    users = request.app.database["users"]
    user = users.find_one({"_id": token_data["id"]})

    if not user:
        request.app.logger.info(f"User not found for password reset: {token_data['id']}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="User not found",
        )

    hashed_password = bcrypt.hashpw(credentials.password.encode("utf-8"), bcrypt.gensalt())

    users.update_one(
        {"_id": user["_id"]},
        {"$set": {"password": hashed_password}},
    )

    request.app.logger.info(f"Password reset for user: {user['mail']}")
    return {"detail": "Password reset successfully"}
