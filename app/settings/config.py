from datetime import timedelta
from os import environ
from passlib.context import CryptContext

JWT_SECRET = environ.get("JWT_SECRET", "mysecretkey")
JWT_ALGORITHM = environ.get("JWT_ALGORITHM", "HS256")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
RESET_PASSWORD_EXPIRATION_MINUTES = environ.get("RESET_PASSWORD_EXPIRATION_MINUTES", 60)
EXPIRES = timedelta(minutes=int(RESET_PASSWORD_EXPIRATION_MINUTES))
