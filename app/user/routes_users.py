import logging
from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, Request
from passlib.context import CryptContext
from starlette import status
from starlette.responses import JSONResponse

from app.user.user import UpdateUserRequest, UserBasicCredentials

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


@router.get('/', status_code=status.HTTP_200_OK)
async def get_users(request: Request, mail_filter: Optional[str] = None):
    users = request.app.database["users"]

    # uso las funciones de "agregacion" de Mongo! https://docs.mongodb.com/manual/reference/operator/aggregation-pipeline/
    pipeline = [
        {
            "$limit": 100
        },  # leo 100 usuarios como maximo.. ¿o lo dejamos que lea y muestre todos?
        {
            "$addFields": {"_id": {"$toString": "$_id"}}
        },  # convierto el ObjectID a string
    ]

    if mail_filter:
        pipeline.append({"$match": {"mail": mail_filter}})

    results = list(
        users.aggregate(pipeline)
    )  # al aplicar la agregacion, internamente se hace el find()

    if not results:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="No users found with the specified filters.",
        )
    return results


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
