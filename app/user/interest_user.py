from bson import ObjectId
from fastapi import APIRouter, status, Depends, Request
from pydantic import BaseModel
from starlette.responses import JSONResponse
from app.settings.auth_settings import get_user_id

router_interest = APIRouter()


class UserInterests(BaseModel):
    interests: list[str] = []


@router_interest.get("users/me/interests", status_code=status.HTTP_200_OK)
def get_interests(request: Request, my_user_id: ObjectId = Depends(get_user_id)):
    users = request.app.database["users"]
    my_user = users.find_one({"_id": my_user_id})

    if not my_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": "User not found"}
        )

    return my_user["interests"]


@router_interest.patch("users/me/interests", status_code=status.HTTP_200_OK)
def add_interests(
    request: Request,
    interests: UserInterests,
    my_user_id: ObjectId = Depends(get_user_id),
):
    users = request.app.database["users"]
    my_user = users.find_one({"_id": my_user_id})

    if not my_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": "User not found"}
        )

    users.update_one({"_id": my_user_id}, {"$set": {"interests": interests.interests}})

    return {"message": "Interests updated"}
