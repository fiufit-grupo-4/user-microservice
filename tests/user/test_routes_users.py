from bson import ObjectId
import mongomock
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.settings.auth_settings import Settings
from app.user.utils import ObjectIdPydantic
from app.main import app,logger


client = TestClient(app)


######################################### User examples #########################################

user_1_id_mock = ObjectId()
user_1_mock = {
    "name": "lucas",
    "lastname": "martinez",
    "age": "20",
    "mail": "lucas@gmail.com",
    "encrypted_password": "$2b$12$T3HXmxRONP1sjTkk3Pqaq.9IYl5KNRhMHyJC4QxZPx0AqJpctDqeO",
    "image": "lucas.png",
    "blocked": False,
    "trainings": [],
    "verification": {"verified": False, "video": None}
}


user_2_id_mock = ObjectId()
user_2_mock = {
    "name": "federico",
    "lastname": "pach",
    "age": "20",
    "mail": "fede@gmail.com",
    "encrypted_password": "$3asd2bLF576mxRONP1sjTkk3PqDKq.9IYl5KDsdaJK94KJasdG2ShdlaseO",
    "image": "fede.png",
    "blocked": False,
    "trainings": [],
    "verification": {"verified": False, "video": None}
}


user_3_id_mock = ObjectId()
user_3_mock = {
    "name": "federico",
    "lastname": "pach",
    "age": "20",
    "mail": "fede@gmail.com",
    "encrypted_password": "$3asd2bLF576mxRONP1sjTkk3PqDKq.9IYl5KDsdaJK94KJasdG2ShdlaseO",
    "image": "fede.png",
    "blocked": False,
    "trainings": [],
    "verification": {"verified": False, "video": None}
}


#################################################################################################

@pytest.fixture()
def mongo_mock(monkeypatch):
    mongo_client = mongomock.MongoClient()
    db = mongo_client.get_database("user_microservice")
    col = db.get_collection("users")

    result_1 = col.insert_one(user_1_mock)
    global user_1_inserted_id
    user_1_inserted_id = result_1.inserted_id
    global access_token_user_1
    access_token_user_1 = Settings.generate_token(str(user_1_inserted_id))

    result_2 = col.insert_one(user_2_mock)
    global user_2_inserted_id
    user_2_inserted_id = result_2.inserted_id
    global access_token_user_2
    access_token_user_2 = Settings.generate_token(str(user_2_inserted_id))

    app.database = db
    app.logger = logger

    monkeypatch.setattr(app, "database", db)

#################################################################################################

def test_get_verification_request(mongo_mock):
    admin_mock_id = ObjectId()
    access_token_admin = Settings.generate_token(str(admin_mock_id))

    users = app.database["users"]
    # Sucess
    users.update_one({"_id": user_1_inserted_id}, {"$set": {"verification": {"video": "https//www.media.com/video-user-1", "verified": False}}})
    users.update_one({"_id": user_2_inserted_id}, {"$set": {"verification": {"video": "https//www.media.com/video-user-2", "verified": False}}})

    response = client.get("/users/verification")

    assert response.status_code == status.HTTP_200_OK

    assert response.json()[0].get('id') == str(user_1_inserted_id)
    assert response.json()[0].get('verification').get('video') == 'https//www.media.com/video-user-1'
    assert response.json()[1].get('id') == str(user_2_inserted_id)
    assert response.json()[1].get('verification').get('video') == 'https//www.media.com/video-user-2'



def test_upload_verification_video(mongo_mock):
    # Success: user uploads a video for the first time
    data = {"video": "https//www.media.com/video-user-1"}
    response = client.post(
        f"/users/me/verification",
        headers={"Authorization": f"Bearer {access_token_user_1}"},
        json=data
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == f"User {user_1_inserted_id} verification video was uploaded"
    # Success: same user can still upload a video before getting verified
    response = client.post(
        f"/users/me/verification",
        headers={"Authorization": f"Bearer {access_token_user_1}"},
        json=data
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == f"User {user_1_inserted_id} verification video was uploaded"


def test_approve_verification(mongo_mock):
    # Success: admin approves user verification
    users = app.database["users"]
    users.update_one({"_id": user_1_inserted_id}, {"$set": {"verification": {"video": "https//www.media.com/video-user-1", "verified": False}}})
    response = client.patch(
        f"/users/{user_1_inserted_id}/verification/approve"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == f"User {user_1_inserted_id} verification was approved"

    # Failure: admin tries to approve already verified user
    users.update_one({"_id": user_1_inserted_id}, {"$set": {"verification": {"verified": True}}})
    response = client.patch(
        f"/users/{user_1_inserted_id}/verification/approve"
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == f"User {user_1_inserted_id} already verified"

    # Failure: user not found to verify
    some_user_id = ObjectId()
    response = client.patch(
        f"/users/{some_user_id}/verification/approve"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == f"User {some_user_id} not found to verify"

    # Failure: user verification not found to verify
    users.update_one({"_id": user_1_inserted_id}, {"$set": {"verification": None}})
    response = client.patch(
        f"/users/{user_1_inserted_id}/verification/approve"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == f"User {user_1_inserted_id} verification not found to verify"


def test_reject_verification(mongo_mock):
    # Success: admin rejects user verification
    users = app.database["users"]
    users.update_one({"_id": user_1_inserted_id}, {"$set": {"verification": {"video": "https//www.media.com/video-user-1", "verified": None}}})
    response = client.patch(
        f"/users/{user_1_inserted_id}/verification/reject"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == f"User {user_1_inserted_id} verification was rejected"

    # Failure: admin tries to reject already verified user
    users.update_one({"_id": user_1_inserted_id}, {"$set": {"verification": {"verified": True}}})
    response = client.patch(
        f"/users/{user_1_inserted_id}/verification/reject"
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == f"User {user_1_inserted_id} already verified"

    # Failure: user not found to verify
    some_user_id = ObjectId()
    response = client.patch(
        f"/users/{some_user_id}/verification/reject"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == f"User {some_user_id} not found to verify"

    # Failure: user verification not found to verify
    users.update_one({"_id": user_1_inserted_id}, {"$set": {"verification": None}})
    response = client.patch(
        f"/users/{user_1_inserted_id}/verification/reject"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == f"User {user_1_inserted_id} verification not found to verify"

