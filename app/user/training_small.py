import app.main as main
from app.services import ServiceTrainers
from app.user.utils import ObjectIdPydantic
from bson import ObjectId
from pydantic import BaseConfig, BaseModel


class TrainingResponseUsers(BaseModel):
    id_training: ObjectIdPydantic
    id_trainer: ObjectIdPydantic = None
    title: str
    description: str
    type: str
    difficulty: str

    class Config(BaseConfig):
        json_encoders = {ObjectId: lambda id: str(id)}  # convert ObjectId into str

    @classmethod
    def from_mongo(cls, training: dict):
        if not training:
            return training

        id_training = training.pop('id', None)
        trainer = training.pop('trainer', None)
        if trainer:
            training["id_trainer"] = trainer["id"]

        return cls(**dict(id_training=id_training, **training))
