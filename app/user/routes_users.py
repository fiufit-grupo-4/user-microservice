import logging
from typing import List

from fastapi import APIRouter,Request
from starlette import status
from starlette.responses import JSONResponse
from app.user.user import *

logger = logging.getLogger('app')
router = APIRouter()

@router.post('/', response_description="Create a new user",status_code=status.HTTP_201_CREATED)
async def create_users(request: Request, user_request: UserRequest):

    # How to build a collection
    users = request.app.database["users"]

    if not validate_username(user_request.name, users=users):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=f'User {user_request.name} already exists',
        )
    return create_user(
        user_request.name,
        user_request.lastname,
        user_request.mail,
        user_request.age,
        users,
    )


@router.get('/{user_id}', status_code=status.HTTP_200_OK)
async def get_user(request: Request, user_id: str):
    # How to build a collection
    users = request.app.database["users"]
    if user_id not in users.find():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {user_id} not found',
        )
    return users[user_id]


@router.get('/', status_code=status.HTTP_200_OK)
async def get_users(request: Request,mail_filter: Optional[str] = None):
    users_filtered = []

    # How to build a collection
    users = request.app.database.users

    for p in users.find():
        logger.info(p)
        users_filtered.append(p)

    # users_filtered = list(users.find())
    #
    # if mail_filter:
    #    users_filtered = users.find({"mail": mail_filter})

    return users_filtered


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