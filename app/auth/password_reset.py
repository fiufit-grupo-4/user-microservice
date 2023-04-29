import os
import jwt
from fastapi import Request, status, APIRouter
from fastapi.responses import JSONResponse
from passlib.handlers.bcrypt import bcrypt
from sendgrid import SendGridAPIClient
from starlette.background import BackgroundTasks
from app.user.user import UserBasicCredentials
from app.settings.auth_settings import Settings, JWT_SECRET, JWT_ALGORITHM, generate_token
from sendgrid.helpers.mail import Mail

router = APIRouter()
setting = Settings()


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

    reset_password_url = f"reset_password?token={reset_password_token}"

    background_tasks.add_task(
        send_password_reset_email, to_email=user["mail"], reset_password_url=reset_password_url
    )

    request.app.logger.info(f"Password reset link sent to: {user['mail']}")
    return {"detail": "Password reset link sent"}


def send_password_reset_email(to_email, reset_password_url):
    path = os.environ.get('ENVIROMENT')
    message = Mail(
        from_email='lwaisten@fi.uba.ar',
        to_emails=to_email,
        subject='Reset your password',
        html_content=f'Click <a href="{path}{reset_password_url}">here</a> to reset your password'
    )
    try:

        sg = SendGridAPIClient('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')
        response = sg.send(message)
        print(response.satus_code)
        print(response.body)
        print(response.headers)
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
