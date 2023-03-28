import uuid
from fastapi import FastAPI, status, requests
from pydantic.main import BaseModel
from pydantic import EmailStr
from typing import Optional
from starlette.responses import JSONResponse
from user import *

app = FastAPI()
users = {}


class UserRequest(BaseModel):
    username: str
    email: Optional[EmailStr]


class UserResponse(BaseModel):
    user_id: str
    name: str
    mail: Optional[EmailStr]

    class Config:
        orm_mode = True


def validate_username(username, users):
    for user in users.values():
        if user.name == username:
            return False
    return True

#  name, lastname, age, mail, password)


def create_user(name: str, mail: str):
    user_id = str(uuid.uuid4())
    new_user = User(user_id=user_id, name=name, mail=mail)
    users[user_id] = new_user
    return new_user


@app.post('/users', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_users(user_request: UserRequest):
    if not validate_username(user_request.username, users):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=f'User {user_request.username} already exists',)
    return create_user(user_request.username, user_request.email)


