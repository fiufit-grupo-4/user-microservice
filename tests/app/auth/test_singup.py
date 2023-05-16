from unittest import mock

from fastapi.testclient import TestClient
import mongomock
import pytest

from app.domain.UserRoles import UserRoles
from os import environ as env
from app.main import app
from app.main import logger

# TEST
client = TestClient(app)
password = 'titititi'

lucas = {"mail": "lukitas@gmail.com", "password": password, "phone_number": "+5493446570174"}
pepe = {"mail": "pepon@gmail.com", "password": password, "phone_number": "+5493446570174"}
juan = {"mail": "juan@gmail.com", "password": password, "phone_number": "+5493446570174"}

@pytest.fixture()
def twilio_mock(monkeypatch):
    client_twilio_mock = mock.Mock()
    monkeypatch.setattr("app.settings.twilio.client_twilio", client_twilio_mock)
    return client_twilio_mock


# Mock MongoDB
@pytest.fixture()
def mongo_mock(monkeypatch):
    mongo_client = mongomock.MongoClient()
    db = mongo_client.get_database("user_microservice")
    col = db.get_collection("users")
    col.insert_one(juan)
    app.database = db
    app.logger = logger
    monkeypatch.setattr(app, "database", db)


def test_succeed_if_correct_credentials(mongo_mock):
    credentials = {
        "mail": lucas['mail'],
        "password": password,
        "phone_number": lucas['phone_number'],
        "role": UserRoles.ATLETA.value
    }

    response = client.post("/signup/", json=credentials)
    assert response.status_code == 201


def test_fail_if_user_already_exists(mongo_mock):
    credentials = {
        "mail": juan['mail'],
        "password": password,
        "phone_number": juan['phone_number'],
        "role": UserRoles.ATLETA.value
    }

    response = client.post("/signup/", json=credentials)
    assert response.status_code == 409


def test_validation_code(mongo_mock, twilio_mock):
    credentials = {
        "mail": pepe['mail'],
        "password": password,
        "phone_number": pepe['phone_number'],
        "role": UserRoles.ATLETA.value
    }

    client.post("/signup/", json=credentials)
    twilio_mock.verify.v2.services.return_value.verifications.create.assert_called_once()
