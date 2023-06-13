from fastapi.testclient import TestClient
import mongomock
import pytest

from app.domain.UserRoles import UserRoles
from app.main import app
from app.main import logger

# TEST
client = TestClient(app)
password = 'titititi'
encrypted_password = '$2b$12$T3HXmxRONP1sjTkk3Pqaq.9IYl5KNRhMHyJC4QxZPx0AqJpctDqeO'

lucas = {"name": "lucas", "lastname": "martinez", "age": "20", "mail": "waistenlucas@gmail.com",
         "encrypted_password": encrypted_password, "session_token": "token", "role": 3,
         "phone_number": '+5493446570174', "image": "image.png", "blocked": False, "trainings": [],
         "location": {"longitude": float(300), "latitude": float(400)}, "id": "1234", "first_login": True}

juan = {"name": "lucas", "lastname": "lopez", "age": "20", "mail": "lopezlucas@gmail.com",
        "encrypted_password": encrypted_password, "session_token": "token", "role": 3,
        "phone_number": '+5493446570174', "image": "image.png", "blocked": False, "trainings": [],
        "location": {"longitude": float(300), "latitude": float(400)}, "first_login": True}


# Mock MongoDB
@pytest.fixture()
def mongo_mock(monkeypatch):
    mongo_client = mongomock.MongoClient()
    db = mongo_client.get_database("user_microservice")
    col = db.get_collection("users")
    col.insert_one(lucas)

    app.database = db
    app.logger = logger
    monkeypatch.setattr(app, "database", db)


def test_succeed_if_credentials_are_correct(mongo_mock):
    credentials = {
        "mail": lucas['mail'],
    }

    response = client.post("/login/google", json=credentials)
    assert response.status_code == 200


def test_fail_if_unregistered_user(mongo_mock):
    credentials = {
        "mail": "andy@gmail.com",
    }

    response = client.post("/login/google", json=credentials)
    assert response.status_code == 206


def test_succeed_if_correct_credentials(mongo_mock):
    credentials = {
        "mail": juan['mail'],
        "password": password,
        "phone_number": juan['phone_number'],
        "role": UserRoles.ATLETA.value,
        "name": juan['name'],
        "lastname": juan['lastname'],
        "age": juan['age'],
    }

    response = client.post("/signup/google", json=credentials)
    assert response.status_code == 201


def test_fail_if_user_already_exists(mongo_mock):
    credentials = {
        "mail": lucas['mail'],
        "password": password,
        "phone_number": lucas['phone_number'],
        "role": UserRoles.ATLETA.value,
        "name": lucas['name'],
        "lastname": lucas['lastname'],
        "age": lucas['age'],
    }

    response = client.post("/signup/google", json=credentials)
    assert response.status_code == 409
