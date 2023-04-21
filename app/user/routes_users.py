import logging
from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, Query, Request
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse
from typing import List

from app.user.user import UpdateUserRequest, UserBasicCredentials, UserResponse

logger = logging.getLogger('app')
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def user_already_exists(mail, users):
    results = list(
        users.aggregate(
            [{"$addFields": {"_id": {"$toString": "$_id"}}}, {"$match": {"mail": mail}}]
        )
    )
    return len(results) > 0


class QueryParamFilterUser(BaseModel):
    name: str = Query(None, min_length=1, max_length=256)
    lastname: str = Query(None, min_length=1, max_length=256)
    age: str = Query(None, min_length=1, max_length=3)


@router.get('/', response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(request: Request, queries: QueryParamFilterUser = Depends(), limit: int = Query(128, ge=1, le=1024)):
    users = request.app.database["users"]

    user_list = []
    for user in users.find(queries.dict(exclude_none=True)).limit(limit):
        user_list.append(UserResponse.from_mongo(user))

    logger.info(f'Return list of {len(user_list)} users, with query params: {queries.dict(exclude_none=True)}')
    return user_list


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


@router.patch('/{user_id}', status_code=status.HTTP_200_OK)
async def update_users(
    request: Request, user_id: str, update_user_request: UpdateUserRequest
):
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


@router.put("/{mail}", status_code=status.HTTP_200_OK)
def update_user(mail: str, credentials: UserBasicCredentials, request: Request):
    hashed_password = pwd_context.hash(credentials.password)

    users = request.app.database["users"]
    result = users.update_one({"mail": mail}, {"$set": {"password": hashed_password}})

    if result.modified_count == 1:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=f'User {mail} updated successfully',
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {mail} not found',
        )


@router.delete("/{mail}", status_code=status.HTTP_200_OK)
def delete_user(mail: str, request: Request):
    users = request.app.database["users"]
    result = users.delete_one({"mail": mail})

    if result.deleted_count == 1:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=f'User {mail} deleted successfully',
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {mail} not found',
        )
