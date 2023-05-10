import logging
from bson import ObjectId
from fastapi import APIRouter, status, Depends
from fastapi import Request
from starlette.responses import JSONResponse
from app.domain.UserRoles import UserRoles
from app.settings.auth_settings import get_user_id
from app.user.utils import ObjectIdPydantic

logger = logging.getLogger("app")
router = APIRouter()


def update_user_block_status(
    user_id: ObjectIdPydantic,
    request: Request,
    my_user_id: ObjectId = Depends(get_user_id),
    block: bool = True,
    content: str = "",
):
    users = request.app.database["users"]
    user = users.find_one({"_id": user_id})
    my_own_user = users.find_one({"_id": my_user_id})

    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": "User not found"}
        )

    if my_own_user["role"] != UserRoles.ADMIN.value:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials"},
        )

    if block and user["blocked"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "User is already blocked"},
        )

    if not block and not user["blocked"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "User is not blocked"},
        )

    user["blocked"] = block
    users.update_one({"_id": user_id}, {"$set": {"blocked": block}})

    logger.info(f"User {'blocked' if block else 'unblocked'}: {user_id}")
    return {"message": content}


@router.patch("/{user_id}/block", status_code=status.HTTP_200_OK)
def block_user(
    user_id: ObjectIdPydantic,
    request: Request,
    my_user_id: ObjectId = Depends(get_user_id),
):
    return update_user_block_status(
        user_id, request, my_user_id, block=True, content="User blocked successfully"
    )


@router.patch("/{user_id}/unblock", status_code=status.HTTP_200_OK)
def unblock_user(
    user_id: ObjectIdPydantic,
    request: Request,
    my_user_id: ObjectId = Depends(get_user_id),
):
    return update_user_block_status(
        user_id, request, my_user_id, block=False, content="User unblocked successfully"
    )
