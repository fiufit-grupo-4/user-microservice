from dotenv import load_dotenv
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from firebase_admin import auth

from app.user.user import UserResponse
from app.definitions import GOOGLE_SIGNUP

load_dotenv()
router = APIRouter()


@router.post("/google", status_code=status.HTTP_201_CREATED)
def signup_with_google(token: str, request: Request):

    users = request.app.database["users"]

    try:
        # Verificar el token de Google y obtener los datos del usuario
        id_info = auth.verify_id_token(token)
        google_user_id = id_info['sub']
        google_email = id_info['email']

        # Verificar si el usuario ya existe en tu base de datos
        if users.find_one({"google_user_id": google_user_id}):
            request.app.logger.info(f"User {google_email} already exists")
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=f'User {google_email} already exists',
            )

        # Crear el usuario en tu base de datos
        user = {
            "google_user_id": google_user_id,
            "mail": google_email,
            # Otros datos del usuario que desees almacenar
        }
        user_id = users.insert_one(user).inserted_id

        request.app.logger.info(
            f"User {UserResponse(id=str(user_id), mail=google_email)} successfully created"
        )

        request.state.metrics_allowed = True
        request.state.user_id = user_id
        request.state.action = GOOGLE_SIGNUP
        # request.state.location = user.location
        # TODO

        return UserResponse(id=str(user_id), mail=google_email)

    except Exception as e:
        # Manejo de errores en caso de fallar la autenticación con Google o la creación del usuario en tu base de datos
        request.app.logger.error(f"Error signing up with Google: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content="Error signing up with Google",
        )
