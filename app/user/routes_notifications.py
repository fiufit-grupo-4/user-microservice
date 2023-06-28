import logging
from fastapi import APIRouter, Request
from starlette import status
from starlette.responses import JSONResponse
from app.user.follow_user import router as send_push_notification

from app.user.user import GoalCompletedNotification, MessageNotification

logger = logging.getLogger('app')
router_notifications = APIRouter()


@router_notifications.post('/message/send', status_code=status.HTTP_200_OK)
async def send_new_message(request: Request, message: MessageNotification):
    users = request.app.database["users"]
    user_sender = users.find_one({"_id": message.id_sender})
    user_receiver = users.find_one({"_id": message.id_receiver})
    if not user_receiver:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=f'User {message.id_receiver} does not exist',
        )
    if not user_sender:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=f'User {message.id_sender} does not exist',
        )

    user_receiver_token = user_receiver['device_token']
    title = (
        f"{user_sender['name']} {user_sender['lastname']} has sent you a new message"
    )
    body = message.message

    try:
        send_push_notification(user_receiver_token, title, body)
    except Exception as e:
        logger.error(
            f'Error sending push notification (title={title}, body={body}) to device token: {user_receiver_token} with error: {e}'
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content='Error in system notification',
        )

    logger.info(
        f'Notification of new message sent successfully from {message.id_sender} to {message.id_receiver}'
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=f"Notification of new message sent successfully from {message.id_sender} to {message.id_receiver}",
    )


@router_notifications.post('/goal/completed/send', status_code=status.HTTP_200_OK)
async def send_new_goal_completed(request: Request, message: GoalCompletedNotification):
    users = request.app.database["users"]
    user_receiver = users.find_one({"_id": message.id_receiver})
    if not user_receiver:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=f'User {message.id_receiver} does not exist',
        )

    user_receiver_token = user_receiver['device_token']
    title = "Goal accomplished"
    body = f"Completed the goal {message.title_goal}"

    try:
        send_push_notification(user_receiver_token, title, body)
        users.update_one(
            {"_id": message.id_receiver},
            {"$push": {"notifications": {"title": title, "body": body}}},
        )
    except Exception as e:
        logger.error(
            f'Error sending push notification (title={title}, body={body}) to device token: {user_receiver_token} with error: {e}'
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content='Error in system notification',
        )

    logger.info(
        f'Notification of Goal Completed sent successfully to {message.id_receiver}'
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=f"Notification of Goal Completed sent successfully to {message.id_receiver}",
    )
