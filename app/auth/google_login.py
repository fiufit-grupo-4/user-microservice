import logging
import firebase_admin
from firebase_admin import auth
from fastapi import APIRouter, HTTPException, status
from firebase_admin.auth import InvalidIdTokenError
from pydantic import BaseModel
from starlette.responses import JSONResponse

from app.settings.auth_settings import generate_token

router = APIRouter()
logger = logging.getLogger("app")


class GoogleLoginRequest(BaseModel):
    id_token: str


@router.post("/google")
def login_google(request: GoogleLoginRequest):
    try:
        # Verificar el token de acceso con Firebase Admin
        decoded_token = auth.verify_id_token(request.id_token)
        # Obtener el ID de usuario del token decodificado
        user_id = decoded_token['uid']
        # Realizar cualquier validación adicional necesaria

        # Aquí puedes realizar la lógica para autenticar al usuario en tu sistema y generar un token de acceso personalizado
        # Puedes generar el token de acceso utilizando JWT o cualquier otro método de autenticación personalizado
        # Generar el token de acceso
        access_token = generate_token(str(user_id), "TODO")

        # Ejemplo de respuesta exitosa
        return {"access_token": access_token, "token_type": "bearer"}

    except InvalidIdTokenError as e:
        # El token de acceso es inválido
        logger.error(f"Invalid access token with Google: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token"
        )
    except Exception as e:
        # Ocurrió un error durante el proceso de inicio de sesión
        logger.error(f"Error login with Google: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content="Error login with Google",
        )


# Inicializar Firebase Admin
firebase_admin.initialize_app()
