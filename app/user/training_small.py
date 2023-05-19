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

    @classmethod
    async def from_service(cls, id_user, id_training):
        training = await ServiceTrainers.get(f'/trainings/{id_training}')

        if training.status_code == 200:
            training = training.json()
            return TrainingResponseUsers.from_mongo(training)
        elif training.status_code == 404:
            users = main.app.database["users"]
            users.update_one({"_id": id_user}, {"$pull": {"trainings": id_training}})
        else:
            return None
