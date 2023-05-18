from fastapi.testclient import TestClient
import mongomock
import pytest

from app.main import app
from app.main import logger

# TEST
client = TestClient(app)
password = 'titititi'
encrypted_password = '$2b$12$T3HXmxRONP1sjTkk3Pqaq.9IYl5KNRhMHyJC4QxZPx0AqJpctDqeO'

atleta = {"name": "lucas", "lastname": "martinez", "age": "20", "mail": "waistenlucas@gmail.com",
          "encrypted_password": encrypted_password, "session_token": "token", "role": 3,
          "phone_number": '+5493446570174', "image": "image.png", "blocked": False, "trainings": [],
          "location": {"longitude": float(300), "latitude": float(400)}}

blocked_user = {"name": "lucas", "lastname": "lopez", "age": "20", "mail": "lopezlucas@gmail.com",
                "encrypted_password": encrypted_password, "session_token": "token", "role": 3,
                "phone_number": '+5493446570174', "image": "image.png", "blocked": True, "trainings": [],
                "location": {"longitude": float(300), "latitude": float(400)}}


# Mock MongoDB
@pytest.fixture()
def mongo_mock(monkeypatch):
    mongo_client = mongomock.MongoClient()
    db = mongo_client.get_database("user_microservice")
    col = db.get_collection("users")
    col.insert_one(atleta)

    app.database = db
    app.logger = logger
    monkeypatch.setattr(app, "database", db)


def test_succeed_if_credentials_are_correct(mongo_mock):
    credentials = {
        "mail": atleta['mail'],
        "password": password,
        "role": 3
    }

    response = client.post("/login/", json=credentials)
    assert response.status_code == 200


def test_fail_if_unregistered_user(mongo_mock):
    credentials = {
        "mail": "andy@gmail.com",
        "password": password,
        "role": 3
    }

    response = client.post("/login/", json=credentials)
    assert response.status_code == 401


def test_fail_if_wrong_password(mongo_mock):
    credentials = {
        "mail": atleta['mail'],
        "password": "wrong_password",
        "role": 3
    }

    response = client.post("/login/", json=credentials)
    assert response.status_code == 401


def test_fail_if_wrong_role(mongo_mock):
    credentials = {
        "mail": atleta['mail'],
        "password": password,
        "role": 1
    }

    response = client.post("/login/", json=credentials)
    assert response.status_code == 401


def test_fail_if_blocked(mongo_mock):
    credentials = {
        "mail": blocked_user['mail'],
        "password": password,
        "phone_number": blocked_user['phone_number'],
        "role": 3
    }

    response = client.post("/login/", json=credentials)
    assert response.status_code == 401
