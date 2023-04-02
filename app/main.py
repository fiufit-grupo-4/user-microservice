import uuid
from pydantic.main import BaseModel
from pydantic import EmailStr
from typing import Optional
from starlette.responses import JSONResponse
from app.user.user import User
import pymongo
from fastapi import FastAPI, HTTPException, status, APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext

import logging
from logging.config import dictConfig
from .log_config import logconfig
from os import environ

MONGODB_URI = environ["MONGODB_URI"]

dictConfig(logconfig)
app = FastAPI()
users = {}
logger = logging.getLogger('app')

logger.error("Error message! - Level 3")
logger.warning("Warning message! - Level 2")
logger.info("Info message! - Level 1")
logger.debug("Debug message! - Level 0")


class UserRequest(BaseModel):
    name: str
    lastname: str
    mail: Optional[EmailStr]
    age: str


class UserResponse(BaseModel):
    user_id: str
    name: str
    lastname: str
    age: str
    mail: Optional[EmailStr]

    class Config:
        orm_mode = True


class UpdateUserRequest(BaseModel):
    mail: EmailStr


def validate_username(username, data_base):
    for user in data_base.values():
        if user.name == username:
            return False
    return True


def create_user(name: str, lastname: str, mail: str, age: str, data_base):
    user_id = str(uuid.uuid4())
    new_user = User(user_id=user_id, name=name, lastname=lastname, mail=mail, age=age)
    data_base[user_id] = new_user
    return new_user


@app.get("/", tags=["Home"])
def get_root() -> dict:
    return {"message": "OK"}


@app.on_event("startup")
async def startup_db_client():
    try:
        app.mongodb_client = pymongo.MongoClient(MONGODB_URI)
        logger.info("Connected successfully MongoDB")

    except Exception as e:
        logger.error(e)
        logger.error("Could not connect to MongoDB")

    # How to build a collection
    db = app.mongodb_client["example-db"]
    collection = db.example_collection

    collection.delete_many({})  # Clear collection data

    # Add data to collection
    person_1 = {"name": "Agustin", "age": {"$numberInt": "99"}}
    logger.info("Added object with id: %s", collection.insert_one(person_1).inserted_id)
    person_2 = {"name": "Alfonso", "age": {"$numberInt": "10"}}
    logger.info("Added object with id: %s", collection.insert_one(person_2).inserted_id)

    # Check all data in collection
    for p in collection.find():
        logger.warning(p)


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    logger.info("Shutdown APP")


@app.post('/users', status_code=status.HTTP_201_CREATED, tags=["User-Microservice"])
async def create_users(user_request: UserRequest):
    if not validate_username(user_request.name, data_base=users):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=f'User {user_request.name} already exists',
        )
    return create_user(
        user_request.name,
        user_request.lastname,
        user_request.mail,
        user_request.age,
        users,
    )


@app.get('/users/{user_id}', status_code=status.HTTP_200_OK, tags=["User-Microservice"])
async def get_user(user_id: str):
    if user_id not in users:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {user_id} not found',
        )
    return users[user_id]


@app.get('/users', status_code=status.HTTP_200_OK, tags=["User-Microservice"])
async def get_users(mail_filter: Optional[str] = None):
    users_filtered = []
    for user_id, user in users.items():
        if mail_filter:
            if mail_filter in user.mail:
                users_filtered.append(user)
        else:
            users_filtered.append(user)
    return users_filtered


@app.patch(
    '/users/{user_id}', status_code=status.HTTP_202_ACCEPTED, tags=["User-Microservice"]
)
async def update_users(user_id: str, update_user_request: UpdateUserRequest):
    if user_id not in users:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {user_id} not found',
        )
    user = users[user_id]
    user.mail = update_user_request.mail
    users[user_id] = user
    return user


### LOGIN USER ###

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


@app.post("/login", tags=["User-Microservice"])
def login(credentials: HTTPBasicCredentials):
    user = get_user(credentials.username)
    print("\n USUARIO" + user)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username")
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid password")
    return {"username": user["username"], "email": user["email"]}
