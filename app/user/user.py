
import asyncio
from typing import Optional, Union
from bson import ObjectId
from fastapi import HTTPException, Query
from pydantic import BaseConfig, BaseModel, EmailStr, Field
from app.domain.UserRoles import UserRoles
from app.services import ServiceTrainers
from app.user.training_small import TrainingResponseUsers
from app.user.utils import ObjectIdPydantic

import app.main as main


def create_user(name: str, lastname: str, mail: str, age: str):
    new_user = User(name=name, lastname=lastname, mail=mail, age=age)
    return new_user


class LocationResponse(BaseModel):
    latitude: float = Field(example="400")
    longitude: float = Field(example="350")


class Verification(BaseModel):
    verified: bool = None
    video: str = None


class UserSignUpCredentials(BaseModel):
    mail: EmailStr = Field(example="username@mail.com")
    password: str = Field(example="secure")
    phone_number: str = Field(example="+543446570174")
    role: int = Field(example=3)
    name: str = Field(example='user')
    lastname: str = Field(example='name')
    age: str = Field(example='20')
    location: Optional[LocationResponse]
    image: Optional[str] = None


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
    trainings: Optional[list[Union[TrainingResponseUsers, dict]]]
    blocked: Optional[bool]
    first_login: Optional[bool]
    location: Optional[LocationResponse]
    following: Optional[list[str]]
    followers: Optional[list[str]]
    verification: Optional[Verification]
    device_token: Optional[str]
    interest: Optional[list[str]]

    class Config(BaseConfig):
        json_encoders = {ObjectId: lambda id: str(id)}  # convert ObjectId into str

    @staticmethod
    async def map_trainings(user_list):
        """Map "trainigs ids" to "trainings data" for each user in user_list"""

        trainings_tasks = UserResponse.prepare_training_tasks(user_list)

        main.app.logger.info(
            f'Waiting for {len(trainings_tasks)} \"GET /trainings/{{id_training}}\" requests'
        )

        # Wait in parallel for all requests to finish
        training_responses = await asyncio.gather(*trainings_tasks.values())

        trainings = UserResponse.reorganize_trainings(
            trainings_tasks, training_responses
        )

        UserResponse.convert_all_types_ids(user_list, trainings)

    @staticmethod
    def convert_all_types_ids(user_list, trainings):
        """With the trainings data, map all the ids trainings of each user in the list."""

        for user in user_list:
            new_list_trainings = []
            for old_training in user.trainings:
                new_training = trainings[old_training["id_training"]]
                if new_training:
                    new_list_trainings.append(
                        TrainingResponseUsers.from_mongo(new_training.copy())
                    )
                else:
                    main.app.logger.warning(
                        f'DELETING TRAINING OLD {old_training["id_training"]} FROM USER {user.id}'
                    )
                    users = main.app.database["users"]
                    users.update_one(
                        {"_id": user.id},
                        {"$pull": {"trainings": ObjectId(old_training["id_training"])}},
                    )

            user.trainings = new_list_trainings

    @staticmethod
    def reorganize_trainings(trainings_tasks, res):
        """Reorganize the trainings in a dict with the id as key, and the training (obtained in
        the request) as value. If the training does not exist, the value assigned is None"""

        trainings = {}
        for id_training, training in zip(trainings_tasks.keys(), res):
            if training.status_code == 200:
                trainings[id_training] = training.json()
            elif training.status_code == 404:
                main.app.logger.warning(f'Training with id {training} not found')
                trainings[id_training] = None
            else:
                main.app.logger.error(
                    f'Error getting training: {training.status_code} {training.json()}'
                )
                raise HTTPException(
                    status_code=training.status_code,
                    detail='Error getting training for any user',
                )

        main.app.logger.info(
            f'Finished waiting for {len(trainings_tasks)} \"GET /trainings/{{id_training}}\" requests'
        )

        return trainings

    @staticmethod
    def prepare_training_tasks(user_list):
        """Prepare the tasks (small threads) to get all uniques trainigs of each user in the list.
        The tasks are stored in a dictionary where the key is the id of the training,
        All the tasks are created at the same time, but they are not executed until
        the "await" is called. Thanks to this, the requests are executed in parallel,
        and the time to get all the trainings is reduced."""

        trainings_tasks = {}
        for user in user_list:
            for old_training in user.trainings:
                if old_training["id_training"] not in trainings_tasks:
                    trainings_tasks[old_training["id_training"]] = asyncio.create_task(
                        ServiceTrainers.get(
                            f'/trainings/{old_training["id_training"]}'
                            + '?map_users=false&map_states=false'
                        )
                    )

        return trainings_tasks

    @classmethod
    def from_mongo(cls, user: dict):
        if not user:
            return user

        id_user = str(user.pop('_id', None))
        trainings = user.pop('trainings', [])
        following = user.pop('following', [])
        followers = user.pop('followers', [])
        interest = user.pop('interest', [])

        following_response = [str(f_id) for f_id in following]
        followers_response = [str(f_id) for f_id in followers]
        training_responses = [{"id_training": str(t_id)} for t_id in trainings]

        # Using a dictionary comprehension instead of the dict constructor
        user_dict = {
            **user,
            'id': id_user,
            'trainings': training_responses,
            'followers': followers_response,
            'following': following_response,
            'interest': interest,
        }
        return cls(**user_dict)


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
    device_token: Optional[str]


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
        first_login=True,
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
        self.first_login = first_login

        self.trainings = []
        self.following = []
        self.followers = []
        self.interest = []
        self.verification = Verification()
        self.device_token = None
