from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse
from app.settings.auth_settings import Settings, pwd_context
from app.user.user import User, UserBasicCredentials, UserResponse

router = APIRouter()
setting = Settings()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(credentials: UserBasicCredentials, request: Request):
    hashed_password = pwd_context.hash(credentials.password)
    user = User(credentials.mail, hashed_password, role=credentials.role)

    users = request.app.database["users"]

    if users.find_one({"mail": credentials.mail}, {"_id": 0}):
        request.app.logger.info(f"User {credentials.mail} already exists")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=f'User {credentials.mail} already exists',
        )
    user_id = users.insert_one(jsonable_encoder(user)).inserted_id

    request.app.logger.info(
        f"User {UserResponse(id=str(user_id), mail=user.mail)} successfully created"
    )
    return UserResponse(id=str(user_id), mail=user.mail)
