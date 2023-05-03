from twilio.rest import Client
import os
from fastapi import Request, status, APIRouter
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTasks
from app.user.user import UserForgotPasswordCredential, UserResetPasswordCredential
from app.settings.auth_settings import Settings, pwd_context

router = APIRouter()
setting = Settings()
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client_twilio = Client(account_sid, auth_token)


@router.post("/forgot_password", status_code=status.HTTP_200_OK)
async def forgot_password(
    credentials: UserForgotPasswordCredential,
    background_tasks: BackgroundTasks,
    request: Request,
):
    users = request.app.database["users"]
    user = users.find_one({"mail": credentials.mail})

    if not user:
        request.app.logger.info(f"User not found: {credentials.mail}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="User not found",
        )

    background_tasks.add_task(send_password_reset_email, to_email=user["mail"])

    request.app.logger.info(f"Password reset link sent to: {user['mail']}")
    return {"detail": "Password reset link sent"}


def send_password_reset_email(to_email):
    verification = client_twilio.verify.v2.services(
        os.environ.get('TWILIO_SERVICES')
    ).verifications.create(
        channel_configuration={
            'template_id': os.environ.get('SENGRID_EMAIL_TEMPLATE_ID'),
            'from': 'lwaisten@fi.uba.ar',
            'from_name': 'Lucas Waisten',
        },
        to=to_email,
        channel='email',
    )

    print(verification)


@router.post("/reset_password/{validation_token}", status_code=status.HTTP_200_OK)
async def reset_password(
    credentials: UserResetPasswordCredential, validation_code: str, request: Request
):
    try:
        client_twilio.verify.v2.services(
            os.environ.get('TWILIO_SERVICES')
        ).verification_checks.create(to=credentials.mail, code=validation_code)
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Invalid verification code or email",
        )

    users = request.app.database["users"]
    user = users.find_one({"mail": credentials.mail})

    if not user:
        request.app.logger.info(
            f"User not found for password reset: {credentials.mail}"
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="User not found, email not registred",
        )

    hashed_password = pwd_context.hash(credentials.new_password)

    users.update_one(
        {"_id": user["_id"]},
        {"$set": {"encrypted_password": hashed_password}},
    )
    request.app.logger.info(users.find_one({"mail": credentials.mail}))
    request.app.logger.info(f"Password reset for user: {user['mail']}")

    return {"detail": "Password reset successfully"}
