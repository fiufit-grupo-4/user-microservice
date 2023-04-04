from http.client import HTTPException
from fastapi import APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext

router = APIRouter()

security = HTTPBasic()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_login = {
    "foo": {
        "username": "foo",
        "full_name": "Lucas",
        "email": "ss@gmail.com",
        "hashed_password": "pepe",
    }
}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str):
    if username in users_login:
        user_dict = users_login[username]
        return user_dict
    return None


@router.post("/")
def login(credentials: HTTPBasicCredentials):
    user = get_user(credentials.username)
    print("\n USUARIO" + user)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username")
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid password")
    return {"username": user["username"], "email": user["email"]}