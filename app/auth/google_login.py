import google
from fastapi import Request, Response, status, APIRouter
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token
from google.auth.transport.requests import Request as AuthRequest

router = APIRouter()


@router.get("google")
async def login_with_google(request: Request):
    # Crea una URL de inicio de sesión de Google que solicite acceso a la información del perfil y del correo electrónico del usuario
    google_auth_url, state = google.oauth2.authorization_url(
        "https://accounts.google.com/o/oauth2/auth",
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        scope=["openid", "email", "profile"],
    )

    # Almacena el estado en una cookie para validar la respuesta
    response = RedirectResponse(url=google_auth_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="oauth_state", value=state)
    return response


@router.get("/google/callback")
async def google_callback(
    request: Request, response: Response, code: str = None, state: str = None
):
    # Valida el estado de la cookie
    if request.cookies.get("oauth_state") != state:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Invalid state parameter"}

    # Intercambia el código de autorización por un token de acceso de Google
    google_token = google.oauth2.fetch_token(
        "https://accounts.google.com/o/oauth2/token",
        authorization_response=request.url,
        client_secret="google_client_secret",
    )

    # Valida el token de acceso con Google
    try:
        id_info = id_token.verify_oauth2_token(google_token["id_token"], AuthRequest())
    except ValueError:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unable to validate token"}

    # Inicia sesión en la cuenta del usuario
    user_id = id_info["sub"]
    # Aquí se implementaría el código para iniciar sesión en la cuenta del usuario y redirigirlo a las funcionalidades del sistema.
    return {"message": f"Logged in as user {user_id}"}
