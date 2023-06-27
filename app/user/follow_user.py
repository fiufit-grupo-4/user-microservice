import logging

from bson import ObjectId
from fastapi import APIRouter, Depends, Request
from starlette import status
from starlette.responses import JSONResponse
from firebase_admin import messaging

from app.settings.auth_settings import get_user_id
from app.user.utils import ObjectIdPydantic

logger = logging.getLogger('app')
router = APIRouter()


def send_push_notification(device_token, title, body):
    if device_token is not None:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=device_token,
        )
        messaging.send(message)


@router.post('/{id_user_to_follow}/follow', status_code=status.HTTP_200_OK)
async def follow(
    request: Request,
    id_user_to_follow: ObjectIdPydantic,
    id_user: ObjectId = Depends(get_user_id),
):
    users = request.app.database["users"]
    user_to_follow = users.find_one({"_id": id_user_to_follow})

    if not user_to_follow:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=f'User {id_user_to_follow} does not exist',
        )

    user = users.find_one({"_id": id_user})
    if user:
        if id_user_to_follow in user['following']:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=f'Already following user {id_user_to_follow}',
            )

        users.update_one({"_id": id_user_to_follow}, {"$push": {"followers": id_user}})
        result = users.update_one(
            {"_id": id_user}, {"$push": {"following": id_user_to_follow}}
        )
        if result.modified_count == 1:
            logger.info(f'User {id_user} followed user {id_user_to_follow}')
            users.update_one(
                {"_id": id_user_to_follow},
                {
                    "$push": {
                        "notifications": {
                            "title": 'New follower',
                            "body": f"El usuario {user['name']} {user['lastname']} a comenzado a seguirte",
                        }
                    }
                },
            )
            send_push_notification(
                device_token=user_to_follow['device_token'],
                title='New follower',
                body=f'El usuario {id_user} a comenzado a seguirte',
            )
            return JSONResponse(status_code=status.HTTP_200_OK)
        else:
            logger.info(f'Failed to unfollow {id_user_to_follow}')
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=f'Failed to unfollow {id_user_to_follow}',
            )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content='User does not exist'
    )


@router.post('/{id_user_to_unfollow}/unfollow', status_code=status.HTTP_200_OK)
async def unfollow(
    request: Request,
    id_user_to_unfollow: ObjectIdPydantic,
    id_user: ObjectId = Depends(get_user_id),
):
    users = request.app.database["users"]
    user_to_unfollow = users.find_one({"_id": id_user_to_unfollow})

    if not user_to_unfollow:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=f'User {id_user_to_unfollow} does not exist',
        )

    user = users.find_one({"_id": id_user})
    if user:
        if id_user_to_unfollow in user['following']:
            users.update_one(
                {"_id": id_user_to_unfollow}, {"$pull": {"followers": id_user}}
            )
            result = users.update_one(
                {"_id": id_user}, {"$pull": {"following": id_user_to_unfollow}}
            )
            if result.modified_count == 1:
                logger.info(f'User {id_user} unfollowed {id_user_to_unfollow}')
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=f'User {id_user} unfollowed {id_user_to_unfollow}',
                )
            else:
                logger.info(f'Failed to unfollow {id_user_to_unfollow}')
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=f'Failed to unfollow {id_user_to_unfollow}',
                )
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content='User does not exist'
        )
