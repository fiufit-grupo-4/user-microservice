from typing import Optional
from pydantic import BaseModel, EmailStr, Field


def create_user(name: str, lastname: str, mail: str, age: str):
    new_user = User(name=name, lastname=lastname, mail=mail, age=age)
    return new_user


class UserBasicCredentials(BaseModel):
    mail: EmailStr = Field(example="username@mail.com")
    password: str = Field(example="secure")


class UserRequest(BaseModel):
    name: str
    lastname: str
    mail: Optional[EmailStr]
    age: str


class UserResponse(BaseModel):
    id: str
    name: Optional[str]
    lastname: Optional[str]
    age: Optional[int]
    mail: EmailStr

    class Config:
        orm_mode = True


class UpdateUserRequest(BaseModel):
    mail: EmailStr


class User:
    def __init__(self, mail, password, name=None, lastname=None, age=None):
        self.name = name
        self.lastname = lastname
        self.age = age
        self.mail = mail
        self.encrypted_password = password
