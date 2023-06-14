from bson import ObjectId
from fastapi import APIRouter, status, Depends, Request
from pydantic import BaseModel
from starlette.responses import JSONResponse
from app.settings.auth_settings import get_user_id
import logging

router_interest = APIRouter()
logger = logging.getLogger("app")


class RequestInterests(BaseModel):
    interest: list[str]


class ResponseInterests(BaseModel):
    interest: list[str]


@router_interest.get("/me/interest", status_code=status.HTTP_200_OK)
def get_interests(request: Request, my_user_id: ObjectId = Depends(get_user_id)):
    users = request.app.database["users"]
    my_user = users.find_one({"_id": my_user_id})

    logger.info(my_user)
    return ResponseInterests(interest=my_user["interest"])


@router_interest.patch("/me/interest", status_code=status.HTTP_200_OK)
def add_interests(
    request: Request,
    userInterest: RequestInterests,
    my_user_id: ObjectId = Depends(get_user_id),
):
    users = request.app.database["users"]
    my_user = users.find_one({"_id": my_user_id})

    logger.info(f'Updating User {my_user} a values of {list(userInterest.interest)}')
    users.update_one({"_id": my_user_id}, {"$set": {"interest": userInterest.interest}})

    return {"message": "Interests updated"}
