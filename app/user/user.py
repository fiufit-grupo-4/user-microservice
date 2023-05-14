from enum import Enum
from logging import Logger
from time import sleep
from typing import Optional
from bson import ObjectId
from fastapi import FastAPI, Query
from pydantic import BaseConfig, BaseModel, EmailStr, Field
import requests
from app.domain.UserRoles import UserRoles
from app.settings.config import TRAINING_SERVICE_URL
from app.user.training_small import TrainingResponse
from app.user.utils import ObjectIdPydantic


def create_user(name: str, lastname: str, mail: str, age: str):
    new_user = User(name=name, lastname=lastname, mail=mail, age=age)
    return new_user


class UserBasicCredentials(BaseModel):
    mail: EmailStr = Field(example="username@mail.com")
    password: str = Field(example="secure")
    phone_numer: str = Field(example="+543446570174")
    role: int = Field(example=3)


class UserForgotPasswordCredential(BaseModel):
    mail: EmailStr = Field(example="username@mail.com")


class UserResetPasswordCredential(BaseModel):
    mail: EmailStr = Field(example="username@mail.com")
    new_password: str = Field(example="secure")


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
    role: Optional[UserRoles]
    phone_number: Optional[str]
    image: Optional[str]
    trainings: Optional[list[TrainingResponse]]
    blocked: Optional[bool]

    class Config(BaseConfig):
        json_encoders = {ObjectId: lambda id: str(id)}  # convert ObjectId into str

    @classmethod
    def from_mongo(cls, user: dict):
        """We must convert _id into "id" and"""
        if not user:
            return user
        id_user = user.pop('_id', None)

        trainings = user.pop('trainings', None)
        trainings = list(
            filter(
                lambda training: training is not None,
                map(
                    lambda id_training: TrainingResponse.from_service(
                        id_user, id_training
                    ),
                    trainings,
                ),
            )
        )

        return cls(**dict(user, id=id_user, trainings=trainings))


class UpdatePutUserRequest(BaseModel):
    name: Optional[str]
    lastname: Optional[str]
    age: Optional[str]
    mail: Optional[EmailStr]
    password: str


class UpdateUserRequest(BaseModel):
    name: Optional[str]
    lastname: Optional[str]
    age: Optional[str]
    mail: Optional[EmailStr]
    password: Optional[str]
    image: Optional[str]


class QueryParamFilterUser(BaseModel):
    name: str = Query(None, min_length=1, max_length=256)
    lastname: str = Query(None, min_length=1, max_length=256)
    age: str = Query(None, min_length=1, max_length=3)


class User:
    def __init__(
        self,
        mail,
        password,
        phone_number,
        role=UserRoles.ATLETA.value,
        name=None,
        lastname=None,
        age=None,
        image=None,
        blocked=False
    ):
        self.name = name
        self.lastname = lastname
        self.age = age
        self.mail = mail
        self.encrypted_password = password
        self.role = role
        self.image = image
        self.blocked = blocked
        self.phone_number = phone_number

        self.trainings = []
