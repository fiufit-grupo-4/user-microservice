from typing import Optional
from bson import ObjectId
from fastapi import Query
from pydantic import BaseConfig, BaseModel, EmailStr, Field
from app.domain.UserRoles import UserRoles
from app.user.training_small import TrainingResponseUsers
from app.user.utils import ObjectIdPydantic


def create_user(name: str, lastname: str, mail: str, age: str):
    new_user = User(name=name, lastname=lastname, mail=mail, age=age)
    return new_user


class LocationResponse(BaseModel):
    latitude: float = Field(example="400")
    longitude: float = Field(example="350")


class UserSignUpCredentials(BaseModel):
    mail: EmailStr = Field(example="username@mail.com")
    password: str = Field(example="secure")
    phone_number: str = Field(example="+543446570174")
    role: int = Field(example=3)
    name: str = Field(example='user')
    lastname: str = Field(example='name')
    age: str = Field(example='20')
    location: Optional[LocationResponse]


class UserLoginCredentials(BaseModel):
    mail: EmailStr = Field(example="username@mail.com")
    password: str = Field(example="secure")
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
    trainings: Optional[list[TrainingResponseUsers]]
    blocked: Optional[bool]
    location: Optional[LocationResponse]

    class Config(BaseConfig):
        json_encoders = {ObjectId: lambda id: str(id)}  # convert ObjectId into str

    @classmethod
    def from_mongo(cls, user: dict):
        """We must convert _id into "id" and"""
        if not user:
            return user
        id_user = user.pop('_id', None)

        trainings = user.pop('trainings', None)
        if trainings is not None:
            trainings = list(
                filter(
                    lambda training: training is not None,
                    map(
                        lambda id_training: TrainingResponseUsers.from_service(
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
    password: Optional[str]
    image: Optional[str]
    location: Optional[LocationResponse]


class QueryParamFilterUser(BaseModel):
    name: str = Query(None, min_length=1, max_length=256)
    lastname: str = Query(None, min_length=1, max_length=256)
    age: str = Query(None, min_length=1, max_length=3)


class Location:
    def __init__(
        self,
        latitude,
        longitude,
    ):
        self.latitude = latitude
        self.longitude = longitude


class VerificationRequest(BaseModel):
    video: str


class Verification(BaseModel):
    verified: bool = False
    video: str = None


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
        blocked=False,
        location=None,
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
        self.location = location

        self.trainings = []
        self.verification = Verification()
