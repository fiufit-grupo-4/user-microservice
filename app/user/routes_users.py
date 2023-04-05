import logging
from typing import List

from bson import ObjectId
from fastapi import APIRouter,Request
from starlette import status
from starlette.responses import JSONResponse
from app.user.user import *

logger = logging.getLogger('app')
router = APIRouter()

def user_already_exists(mail, users):
        return not users.find_one({"mail": mail}) is None


@router.post('/', response_description="Create a new user",status_code=status.HTTP_201_CREATED)
async def create_users(request: Request, user_request: UserRequest):

    # How to build a collection
    users = request.app.database["users"]

    if  user_already_exists(user_request.name, users=users):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=f'User {user_request.name} already exists'
        )
    new_user = jsonable_encoder(create_user(
        user_request.name,
        user_request.lastname,
        user_request.mail,
        user_request.age
    ))
    user_id = str(users.insert_one(new_user).inserted_id)

    logger.info(new_user)

    return UserResponse(user_id, user_request.name, user_request.lastname, user_request.age, user_request.mail)

@router.get('/{user_id}', status_code=status.HTTP_200_OK)
async def get_user(request: Request, user_id: str):
    users = request.app.database["users"]

    user = users.find_one({"_id": ObjectId(user_id)}, {"_id": 0})
    if user:
        return user
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'{user_id} not found',
        )

@router.get('/', status_code=status.HTTP_200_OK)
async def get_users(request: Request,mail_filter: Optional[str] = None):
    users = request.app.database["users"]

    user = users.find_one({"mail": mail_filter}, {"_id": 0})
    if user:
        return user
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'{mail_filter} not found',
        )


@router.patch(
    '/{user_id}', status_code=status.HTTP_202_ACCEPTED)
async def update_users(request: Request, user_id: str, update_user_request: UpdateUserRequest):
    # How to build a collection
    users = request.app.database["users"]

    if user_id not in users.find():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {user_id} not found',
        )
    user = users[user_id]
    user.mail = update_user_request.mail
    users[user_id] = user
    return user