from dotenv import load_dotenv
load_dotenv()
# Mock MongoDB
from bson import ObjectId
import mongomock
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.config.auth_settings import SettingsAuth
from app.main import app, logger

client = TestClient(app)

######################################### User examples #########################################

interest = ["Distancia recorrida", "Calorias quemadas", "Tiempo de entrenamiento"]

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
    "verification": {"verified": False, "video": None},
    "interest": []
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
    "verification": {"verified": False, "video": None},
    "interest": interest
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
    "verification": {"verified": False, "video": None},
    "interest": []
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
    access_token_user_1 = SettingsAuth.generate_token(str(user_1_inserted_id))

    result_2 = col.insert_one(user_2_mock)
    global user_2_inserted_id
    user_2_inserted_id = result_2.inserted_id
    global access_token_user_2
    access_token_user_2 = SettingsAuth.generate_token(str(user_2_inserted_id))

    app.database = db
    app.logger = logger

    monkeypatch.setattr(app, "database", db)


#################################################################################################

def test_get_my_user_1_interest(mongo_mock):
    response = client.get(
        f"/users/me/interest",
        headers={"Authorization": f"Bearer {access_token_user_1}"},
    )
    assert response.status_code == status.HTTP_200_OK

def test_get_my_user_2_interest(mongo_mock):
    response = client.get(
        f"/users/me/interest",
        headers={"Authorization": f"Bearer {access_token_user_2}"},
    )
    assert response.status_code == status.HTTP_200_OK

def test_update_my_user_1_interest(mongo_mock):
    data = {"interest": interest}
    response = client.patch(
        f"/users/me/interest",
        headers={"Authorization": f"Bearer {access_token_user_1}"},
        json=data
    )
    assert response.status_code == status.HTTP_200_OK

def test_update_my_user_2_interest(mongo_mock):
    data = {"interest": interest}
    response = client.patch(
        f"/users/me/interest",
        headers={"Authorization": f"Bearer {access_token_user_1}"},
        json=data
    )
    assert response.status_code == status.HTTP_200_OK