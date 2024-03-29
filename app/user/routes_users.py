import logging
from bson import ObjectId
from fastapi import APIRouter, Depends, Query, Request
from starlette import status
from starlette.responses import JSONResponse
from typing import List, Optional
from app.services import ServiceTrainers
from app.config.auth_settings import get_user_id
from app.config.config import pwd_context
from app.user.block_user import router as block_user
from app.user.follow_user import router as follow_user
from app.user.interest_user import router_interest
from app.user.training_small import TrainingResponseUsers

from app.user.user import (
    QueryParamFilterUser,
    UpdateUserRequest,
    UserResponse,
    VerificationRequest,
)
from app.user.utils import ObjectIdPydantic
from app.definitions import ADD_TRAINING_TO_FAVS, REMOVE_TRAINING_FROM_FAVS, USER_EDIT

logger = logging.getLogger('app')
router = APIRouter()

router.include_router(block_user, tags=["users"], prefix="")
router.include_router(follow_user, tags=["users"], prefix="")
router.include_router(router_interest, tags=["users"], prefix="")


@router.patch('/{user_id}/verification/approve', status_code=status.HTTP_200_OK)
def approve_verification_request(request: Request, user_id: ObjectIdPydantic):
    users = request.app.database["users"]
    user = users.find_one({"_id": user_id})

    if not user:
        logger.info(f'User {user_id} not found to verify')
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {user_id} not found to verify',
        )
    if not user['verification']:
        logger.info(f'User {user_id} verification not found to verify')
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {user_id} verification not found to verify',
        )
    if user['verification']['verified']:
        logger.info(f'User {user_id} already verified')
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=f'User {user_id} already verified',
        )

    result_update = users.update_one(
        {"_id": user_id}, {"$set": {"verification.verified": True}}
    )

    if result_update.modified_count > 0:
        logger.info(f'User {user_id} verification was approved')
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=f'User {user_id} verification was approved',
        )
    logger.info(f'User {user_id} verification was not approved')
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=f'User {user_id} verification was not approved',
    )


@router.patch('/{user_id}/verification/reject', status_code=status.HTTP_200_OK)
def reject_verification_request(request: Request, user_id: ObjectIdPydantic):
    users = request.app.database["users"]
    user = users.find_one({"_id": user_id})

    if not user:
        logger.info(f'User {user_id} not found to verify')
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {user_id} not found to verify',
        )
    if not user['verification']:
        logger.info(f'User {user_id} verification not found to verify')
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {user_id} verification not found to verify',
        )
    if user['verification']['verified']:
        logger.info(f'User {user_id} already verified')
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=f'User {user_id} already verified',
        )
    result_update = users.update_one(
        {"_id": user_id}, {"$set": {"verification.verified": False}}
    )
    if result_update.modified_count > 0:
        logger.info(f'User {user_id} verification was rejected')
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=f'User {user_id} verification was rejected',
        )
    logger.info(f'User {user_id} verification was not rejected')
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=f'User {user_id} verification was not rejected',
    )


@router.get(
    '/verification', response_model=List[UserResponse], status_code=status.HTTP_200_OK
)
async def get_verification_requests(
    request: Request,
    queries: QueryParamFilterUser = Depends(),
    limit: int = Query(128, ge=1, le=1024),
):
    query = {
        '$and': [
            {
                '$or': [
                    {'verification.verified': None},
                    {'verification.verified': False},
                ]
            },
            {'verification.video': {'$ne': None}},
        ]
    }
    users = request.app.database["users"]
    user_list = []
    for user in users.find({**query, **queries.dict(exclude_none=True)}).limit(limit):
        user_list.append(UserResponse.from_mongo(user))

    logger.info(
        f'Return list of {len(user_list)} users, with query params: {queries.dict(exclude_none=True)}'
    )
    return user_list


@router.get('/', response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(
    request: Request,
    queries: QueryParamFilterUser = Depends(),
    limit: int = Query(128, ge=1, le=1024),
    map_trainings: Optional[bool] = False,
):
    users = request.app.database["users"]

    user_list = []
    for user in users.find(queries.dict(exclude_none=True)).limit(limit):
        user_list.append(UserResponse.from_mongo(user))

    if map_trainings:
        await UserResponse.map_trainings(user_list)

    logger.info(
        f'Return list of {len(user_list)} users, with query params: {queries.dict(exclude_none=True)}'
    )
    return user_list


@router.get('/me', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_me(
    request: Request,
    user_id: ObjectId = Depends(get_user_id),
    map_trainings: Optional[bool] = True,
):
    return await get_user(request, user_id, map_trainings)


@router.post(
    '/me/trainings/{id_training}',
    response_model=TrainingResponseUsers,
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

        training = await ServiceTrainers.get(
            f'/trainings/{id_training}' + '?map_users=false&map_states=false'
        )

        if training.status_code == 200:
            training = training.json()
            result = users.update_one(
                {"_id": id_user}, {"$push": {"trainings": id_training}}
            )
            if result.modified_count == 1:
                logger.info(f'User {id_user} added favorite training {id_training}')
                request.state.metrics_allowed = True
                request.state.action = ADD_TRAINING_TO_FAVS
                request.state.user_id = id_user
                request.state.training_id = id_training
                request.state.location = user.get('location')
                return TrainingResponseUsers.from_mongo(training)

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

    if user:
        if id_training in user['trainings']:
            result = users.update_one(
                {"_id": id_user}, {"$pull": {"trainings": id_training}}
            )
            if result.modified_count == 1:
                logger.info(f'User {id_user} deleted favorite training {id_training}')
                request.state.metrics_allowed = True
                request.state.action = REMOVE_TRAINING_FROM_FAVS
                request.state.user_id = id_user
                request.state.training_id = id_training
                request.state.location = user.get('location')
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
async def get_user(
    request: Request, user_id: ObjectIdPydantic, map_trainings: Optional[bool] = True
):
    users = request.app.database["users"]
    user = users.find_one({"_id": user_id})

    if user:
        logger.info(f'Get a user {user_id}')
        res = UserResponse.from_mongo(user)
        if map_trainings:
            await UserResponse.map_trainings([res])

        return res
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

    if 'notifications' in to_change:
        notification = to_change.pop('notifications')
        result_update = users.update_one(
            {"_id": user_id},
            {"$set": to_change, "$push": {"notifications": notification}},
        )

    else:
        result_update = users.update_one({"_id": user_id}, {"$set": to_change})

    if result_update.modified_count > 0:
        request.state.image_edit = False
        request.state.location_edit = False
        logger.info(f'Updating user {user_id} a values of {list(to_change.keys())}')
        location = to_change.get('location')
        if location:
            request.state.metrics_allowed = True
            request.state.location = location
            request.state.location_edit = True
        request.state.action = USER_EDIT
        request.state.user_id = user_id
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


@router.post('/me/verification', status_code=status.HTTP_200_OK)
def upload_verification_video(
    request: Request,
    request_body: VerificationRequest,
    user_id: ObjectId = Depends(get_user_id),
):
    video_upload = request_body.dict(exclude_none=True)

    if not video_upload or len(video_upload) != 1:
        request.app.logger.info('Wrong request body to upload video'),
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content='Wrong request body to upload video',
        )

    if 'video' not in video_upload:
        request.app.logger.info('No video in body to upload')
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content='No video in body to upload',
        )

    users = request.app.database["users"]
    user = users.find_one({"_id": user_id})

    if not user:
        logger.info(f'User {user_id} not found to verify')
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'User {user_id} not found to verify',
        )

    if user["verification"]["verified"]:
        logger.info(f'User {user_id} was already verified')
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=f'User {user_id} was already verified',
        )

    # in verification.video
    result_update = users.update_one(
        {"_id": user_id},
        {"$set": {"verification.video": video_upload["video"]}},
    )
    if result_update.matched_count > 0:
        logger.info(f'User {user_id} verification video was uploaded')
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=f'User {user_id} verification video was uploaded',
        )
    else:
        logger.critical(f'User {user_id} verification video was not uploaded')
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=f'User {user_id} verification video was not uploaded',
        )
