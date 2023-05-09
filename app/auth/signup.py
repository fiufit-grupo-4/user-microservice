from fastapi.encoders import jsonable_encoder
from app.settings.auth_settings import Settings, pwd_context
from app.user.user import User, UserResponse, UserBasicCredentials
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from app.auth.google_singup import router as google_singup_router


router = APIRouter()
setting = Settings()
router.include_router(
    google_singup_router,
    prefix="",
    tags=["singup"],
)


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
