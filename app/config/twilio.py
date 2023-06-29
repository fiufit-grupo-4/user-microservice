from os import environ as env
from starlette import status
from starlette.responses import JSONResponse
from twilio.rest import Client
from app.config.config import Settings

app_settings = Settings()
client_twilio = Client(app_settings.TWILIO_ACCOUNT_SID, app_settings.TWILIO_AUTH_TOKEN)


def send_password_reset_email(to_email):
    try:
        client_twilio.verify.v2.services(
            app_settings.TWILIO_SERVICES
        ).verifications.create(
            channel_configuration={
                'template_id': app_settings.SENGRID_EMAIL_TEMPLATE_ID,
                'from': 'lwaisten@fi.uba.ar',
                'from_name': 'Lucas Waisten',
            },
            to=to_email,
            channel='email',
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Invalid send verification code to email",
        )


def send_whatsapp_validation_code(to_number):
    try:
        client_twilio.verify.v2.services(
            app_settings.TWILIO_SERVICES
        ).verifications.create(
            channel_configuration={
                'template_id': app_settings.SENGRID_EMAIL_TEMPLATE_ID,  # TODO
                'from': 'lwaisten@fi.uba.ar',
                'from_name': 'Lucas Waisten',
            },
            to=to_number,
            channel='whatsapp',
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Invalid send verification code to whatsapp",
        )


async def twilio_validation_code(phone_number, validation_code):
    try:
        check = client_twilio.verify.v2.services(
            app_settings.TWILIO_SERVICES
        ).verification_checks.create(to=phone_number, code=validation_code)
        if check.status != 'approved':
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content="Error occurred while validating verification code",
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK, content="Verification success"
        )

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Error occurred while validating verification code",
        )
