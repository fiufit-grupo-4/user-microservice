import logging
from dotenv import load_dotenv
from fastapi import APIRouter
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import timedelta
import jwt
from fastapi import Request, status
from fastapi.responses import JSONResponse
from passlib.handlers.bcrypt import bcrypt
from starlette.background import BackgroundTasks
from app.user.user import UserBasicCredentials
from app.settings.auth_settings import Settings, RESET_PASSWORD_EXPIRATION_MINUTES, JWT_SECRET, JWT_ALGORITHM, pwd_context

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
        send_password_reset_email, to=user["mail"], reset_password_url=reset_password_url
    )

    request.app.logger.info(f"Password reset link sent to: {user['mail']}")
    return {"detail": "Password reset link sent"}



async def send_password_reset_email(to: str, reset_password_url: str):
    smtp_server = "smtp.gmail.com"
    port = 587  # TLS
    sender_email = "waistenlucas@gmail.com" # dirección desde la que se enviará el correo
    sender_password = "boroviski97" # contraseña del correo electrónico

    message = MIMEMultipart()
    message["Subject"] = "Password reset request"
    message["From"] = sender_email
    message["To"] = to

    # Create the HTML body of the email
    html = f"""\
    <html>
      <body>
        <p>Hi,</p>
        <p>You have requested to reset your password.</p>
        <p>Please follow the link below to reset your password:</p>
        <p><a href="{reset_password_url}">{reset_password_url}</a></p>
        <p>If you did not request this, please ignore this email and your password will remain unchanged.</p>
      </body>
    </html>
    """

    # Attach the HTML body to the email
    message.attach(MIMEText(html, "html"))

    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to, message.as_string())


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
