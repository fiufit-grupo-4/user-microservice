from dotenv import load_dotenv
load_dotenv()
import pytest
from fastapi import status
from unittest.mock import MagicMock, patch
from bson import ObjectId
from app.domain.UserRoles import UserRoles
from app.user.block_user import block_user, unblock_user, update_user_block_status


@pytest.fixture
def mock_users_collection():
    users_collection = MagicMock()
    yield users_collection


@pytest.fixture
def mock_request(mock_users_collection):
    request = MagicMock()
    request.app.database.__getitem__.return_value = mock_users_collection
    return request


def test_update_user_block_status_user_not_found(mock_request):
    user_id = ObjectId()
    my_user_id = ObjectId()
    mock_users_collection = mock_request.app.database['users']
    mock_users_collection.find_one.return_value = None
    response = update_user_block_status(user_id, mock_request, my_user_id)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_user_block_status_invalid_credentials(mock_request):
    user_id = ObjectId()
    my_user_id = ObjectId()
    user = {"_id": user_id, "role": UserRoles.ATLETA.value, "blocked": False}
    my_own_user = {"_id": my_user_id, "role": UserRoles.ATLETA.value}
    mock_users_collection = mock_request.app.database['users']
    mock_users_collection.find_one.side_effect = [user, my_own_user]
    response = update_user_block_status(user_id, mock_request, my_user_id)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_user_block_status_user_already_blocked(mock_request):
    user_id = ObjectId()
    my_user_id = ObjectId()
    user = {"_id": user_id, "role": UserRoles.ADMIN.value, "blocked": True}
    my_own_user = {"_id": my_user_id, "role": UserRoles.ADMIN.value}
    mock_users_collection = mock_request.app.database['users']
    mock_users_collection.find_one.side_effect = [user, my_own_user]
    response = update_user_block_status(user_id, mock_request, my_user_id, block=True)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_user_block_status_user_not_blocked(mock_request):
    user_id = ObjectId()
    my_user_id = ObjectId()
    user = {"_id": user_id, "role": UserRoles.ADMIN.value, "blocked": False}
    my_own_user = {"_id": my_user_id, "role": UserRoles.ADMIN.value}
    mock_users_collection = mock_request.app.database['users']
    mock_users_collection.find_one.side_effect = [user, my_own_user]
    response = update_user_block_status(user_id, mock_request, my_user_id, block=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_user_block_status_block_user_success(mock_request):
    user_id = ObjectId()
    my_user_id = ObjectId()
    user = {"_id": user_id, "role": UserRoles.ADMIN.value, "blocked": False}
    my_own_user = {"_id": my_user_id, "role": UserRoles.ADMIN.value}
    mock_users_collection = mock_request.app.database['users']
    mock_users_collection.find_one.side_effect = [user, my_own_user]
    update_result = MagicMock()
    mock_users_collection.update_one.return_value = update_result
    response = update_user_block_status(user_id, mock_request, my_user_id, block=True, content= "User blocked successfully")
    assert response == {"message": "User blocked successfully"}
    assert update_result.called_once_with({"_id": user_id}, {"$set": {"blocked": True}})


@patch("app.user.block_user.update_user_block_status")
def test_block_user(mock_update_user_block_status, mock_request):
    user_id = ObjectId()
    my_user_id = ObjectId()
    mock_update_user_block_status.return_value = {"message": "User blocked successfully"}
    response = block_user(user_id, mock_request, my_user_id)
    assert response == {"message": "User blocked successfully"}
    mock_update_user_block_status.assert_called_once_with(
        user_id, mock_request, my_user_id, block=True, content="User blocked successfully"
    )


@patch("app.user.block_user.update_user_block_status")
def test_unblock_user(mock_update_user_block_status, mock_request):
    user_id = ObjectId()
    my_user_id = ObjectId()
    mock_update_user_block_status.return_value = {"message": "User unblocked successfully"}
    response = unblock_user(user_id, mock_request, my_user_id)
    assert response == {"message": "User unblocked successfully"}
    mock_update_user_block_status.assert_called_once_with(
        user_id, mock_request, my_user_id, block=False, content="User unblocked successfully"
    )
