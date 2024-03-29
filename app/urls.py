from fastapi import APIRouter
from app.user.routes_users import router as user_router
from app.auth.login import router as login_router
from app.auth.signup import router as signup_router
from app.auth.google_login import router as google_login_router
from app.auth.google_signup import router as google_signup_router
from app.user.routes_notifications import router_notifications

api_router = APIRouter()

api_router.include_router(user_router, tags=["users"], prefix="/users")
api_router.include_router(login_router, tags=["login"], prefix="/login")
api_router.include_router(google_login_router, tags=["login"], prefix="/login")
api_router.include_router(signup_router, tags=["signup"], prefix="/signup")
api_router.include_router(google_signup_router, tags=["signup"], prefix="/signup")
api_router.include_router(
    router_notifications,
    tags=["Notifications System - User microservice"],
    prefix="/notifications",
)
