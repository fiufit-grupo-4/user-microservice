from typing import Optional
from bson import InvalidDocument, ObjectId
from pydantic import BaseConfig, BaseModel, EmailStr, Field
from bson import ObjectId as BaseObjectId

from app.user.utils import ObjectIdPydantic


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
    id: ObjectIdPydantic
    name: Optional[str]
    lastname: Optional[str]
    age: Optional[str]
    mail: EmailStr

    class Config(BaseConfig):
        json_encoders = {
            ObjectId: lambda id: str(id)  # convert ObjectId into str
        }

    @classmethod
    def from_mongo(cls, user: dict):
        """We must convert _id into "id" and"""
        if not user:
            return user
        id = user.pop('_id', None)
        return cls(**dict(user, id=id))


class UpdateUserRequest(BaseModel):
    mail: EmailStr


class User:
    def __init__(self, mail, password, name=None, lastname=None, age=None):
        self.name = name
        self.lastname = lastname
        self.age = age
        self.mail = mail
        self.encrypted_password = password
