import logging
from bson import ObjectId
from fastapi import APIRouter, Depends, Query, Request
from starlette import status
from starlette.responses import JSONResponse
from typing import List
from app.services import ServiceTrainers
from app.settings.auth_settings import get_user_id
from app.settings.config import pwd_context
from app.user.block_user import router as block_user
from app.user.training_small import TrainingResponse

from app.user.user import (
    QueryParamFilterUser,
    UpdateUserRequest,
    UserResponse,
)
from app.user.utils import ObjectIdPydantic

logger = logging.getLogger('app')
router = APIRouter()

router.include_router(block_user, tags=["users"], prefix="")


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


@router.post(
    '/me/trainings/{id_training}',
    response_model=TrainingResponse,
    status_code=status.HTTP_200_OK,
)
async def add_favorite_training(
    request: Request,
    id_training: ObjectIdPydantic,
    id_user: ObjectId = Depends(get_user_id),
):
    users = request.app.database["users"]
    user = users.find_one({"_id": id_user})

    if user:
        if id_training in user['trainings']:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=f'Training {id_training} already exists as favorite in user {id_user}',
            )

        training = ServiceTrainers.get(f'/trainings/{id_training}')
        logger.warning(training)
        if training.status_code == 200:
            training = training.json()
            result = users.update_one(
                {"_id": id_user}, {"$push": {"trainings": id_training}}
            )
            if result.modified_count == 1:
                logger.info(f'User {id_user} added favorite training {id_training}')
                return TrainingResponse.from_mongo(training)

        logger.info(f'Failed to add favorite training {id_training} to user {id_user}')
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=f'Failed to add favorite training {id_training} to user {id_user}',
        )
    else:
        logger.info(f'User {id_user} not found to add favorite training')
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {id_user} not found to add favorite training',
        )


@router.delete('/me/trainings/{id_training}', status_code=status.HTTP_200_OK)
async def delete_favorite_training(
    request: Request,
    id_training: ObjectIdPydantic,
    id_user: ObjectId = Depends(get_user_id),
):
    users = request.app.database["users"]
    user = users.find_one({"_id": id_user})
    logger.warning(user)
    logger.warning(id_training)
    if user:
        if id_training in user['trainings']:
            result = users.update_one(
                {"_id": id_user}, {"$pull": {"trainings": id_training}}
            )
            if result.modified_count == 1:
                logger.info(f'User {id_user} deleted favorite training {id_training}')
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=f'User {id_user} deleted favorite training {id_training}',
                )
            else:
                logger.info(
                    f'Failed to delete favorite training {id_training} from user {id_user}'
                )
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=f'Failed to delete favorite training {id_training} from user {id_user}',
                )
        else:
            logger.info(f'User {id_user} does not have favorite training {id_training}')
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=f'User {id_user} does not have favorite training {id_training}',
            )
    else:
        logger.info(f'User {id_user} not found to delete favorite training')
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {id_user} not found to delete favorite training',
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
