import logging
from bson import ObjectId
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from passlib.context import CryptContext
from starlette import status
from starlette.responses import JSONResponse
from typing import List
from app.settings.auth_settings import JWT_SECRET
from app.settings.auth_baerer import JWTBearer
import jwt

from app.user.user import (
    QueryParamFilterUser,
    UpdatePutUserRequest,
    UpdateUserRequest,
    UserResponse,
)
from app.user.utils import ObjectIdPydantic

logger = logging.getLogger('app')
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_id(token: str = Depends(JWTBearer())) -> ObjectId:
    try:
        token_data_user = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return ObjectId(token_data_user["id"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )


@router.get('/', response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(
    request: Request,
    queries: QueryParamFilterUser = Depends(),
    limit: int = Query(128, ge=1, le=1024),
):
    users = request.app.database["users"]

    user_list = []
    for user in users.find(queries.dict(exclude_none=True)).limit(limit):
        user_list.append(UserResponse.from_mongo(user))

    logger.info(
        f'Return list of {len(user_list)} users, with query params: {queries.dict(exclude_none=True)}'
    )
    return user_list


@router.get('/me', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_me(request: Request, user_id: ObjectId = Depends(get_user_id)):
    users = request.app.database["users"]
    user = users.find_one({"_id": user_id})

    if user:
        logger.info(f'Get a user {user_id}')
        return UserResponse.from_mongo(user)
    else:
        logger.info(f'User {user_id} not found to get')
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {user_id} not found to get',
        )


@router.get('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(request: Request, user_id: ObjectIdPydantic):
    users = request.app.database["users"]
    user = users.find_one({"_id": user_id})

    if user:
        logger.info(f'Get a user {user_id}')
        return UserResponse.from_mongo(user)
    else:
        logger.info(f'User {user_id} not found to get')
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {user_id} not found to get',
        )


@router.patch('/{user_id}', status_code=status.HTTP_200_OK)
async def update_users(
    request: Request, user_id: ObjectIdPydantic, update_user_request: UpdateUserRequest
):
    to_change = update_user_request.dict(exclude_none=True)

    if not to_change or len(to_change) == 0:
        logger.info('No values specified in body to update')
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content='No values specified to update',
        )

    users = request.app.database["users"]
    user = users.find_one({"_id": user_id})
    if not user:
        logger.info(f'User {user_id} not found to update')
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {user_id} not found',
        )

    if 'password' in to_change:
        to_change['encrypted_password'] = pwd_context.hash(to_change['password'])
        to_change.pop('password')

    result_update = users.update_one({"_id": user_id}, {"$set": to_change})

    if result_update.modified_count > 0:
        logger.info(f'Updating user {user_id} a values of {list(to_change.keys())}')
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=f'User {user_id} updated successfully',
        )
    else:
        logger.info(f'User {user_id} not updated')
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=f'User {user_id} not updated',
        )


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(request: Request, user_id: ObjectIdPydantic):
    users = request.app.database["users"]
    result = users.delete_one({"_id": user_id})

    if result.deleted_count == 1:
        logger.info(f'Deleting user {user_id}')
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=f'User {user_id} deleted successfully',
        )
    else:
        logger.info(f'User {user_id} not found to delete')
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {user_id} not found to delete',
        )
