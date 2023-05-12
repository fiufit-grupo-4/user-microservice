from datetime import timedelta
from os import environ
from passlib.context import CryptContext

JWT_SECRET = environ.get("JWT_SECRET", "mysecretkey")
JWT_ALGORITHM = environ.get("JWT_ALGORITHM", "HS256")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
RESET_PASSWORD_EXPIRATION_MINUTES = environ.get("RESET_PASSWORD_EXPIRATION_MINUTES", 60)
EXPIRES = timedelta(minutes=int(RESET_PASSWORD_EXPIRATION_MINUTES))
account_sid = environ.get('TWILIO_ACCOUNT_SID', 'ACe21e9a0fbce06dcd869f1ed2ff3248a5')
auth_token = environ.get('TWILIO_AUTH_TOKEN', '816c7aa1c6ba5946cd4f493ef441e70a')
TRAINING_SERVICE_URL = environ.get(
    'TRAINING_SERVICE_URL', 'http://training-microservice:7501'
)
