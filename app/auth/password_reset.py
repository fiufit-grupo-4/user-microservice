from fastapi import Request, status, APIRouter
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTasks
from app.config.config import pwd_context
from app.config.twilio import send_password_reset_email, twilio_validation_code
from app.user.user import UserForgotPasswordCredential, UserResetPasswordCredential
from app.definitions import PASSWORD_EDIT

router = APIRouter()


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

    request.state.metrics_allowed = True
    request.state.user_id = user['_id']  # TODO: CHECK OR REMOVE _
    request.state.action = PASSWORD_EDIT

    request.app.logger.info(f"Password reset link sent to: {user['mail']}")
    return {"detail": "Password reset link sent"}


@router.post("/reset_password/{validation_code}", status_code=status.HTTP_200_OK)
async def reset_password(
    credentials: UserResetPasswordCredential, validation_code: str, request: Request
):
    try:
        await twilio_validation_code(credentials.mail, validation_code)
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
    # request.state.metrics_allowed = True
    # #TODO
    return {"detail": "Password reset successfully"}
