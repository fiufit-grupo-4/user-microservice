import uuid
from fastapi import FastAPI, status
from pydantic.main import BaseModel
from pydantic import EmailStr
from typing import Optional
from starlette.responses import JSONResponse
from user import *

app = FastAPI()
users = {}


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


@app.post('/users', status_code=status.HTTP_201_CREATED)
async def create_users(user_request: UserRequest):
    if not validate_username(user_request.name, data_base=users):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=f'User {user_request.name} already exists',)
    return create_user(user_request.name, user_request.lastname,user_request.mail, user_request.age, users)


@app.get('/users/{user_id}', status_code=status.HTTP_200_OK)
async def get_user(user_id: str):
    if user_id not in users:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f'User {user_id} not found',)
    return users[user_id]


@app.get('/users', status_code=status.HTTP_200_OK)
async def get_users(mail_filter: Optional[str] = None):
    users_filtered = []
    for user_id, user in users.items():
        if mail_filter:
            if mail_filter in user.mail:
                users_filtered.append(user)
        else:
            users_filtered.append(user)
    return users_filtered


@app.patch('/users/{user_id}', status_code=status.HTTP_202_ACCEPTED)
async def update_users(user_id: str, update_user_request: UpdateUserRequest):
    if user_id not in users:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f'User {user_id} not found',)
    user = users[user_id]
    user.mail = update_user_request.mail
    users[user_id] = user
    return user
