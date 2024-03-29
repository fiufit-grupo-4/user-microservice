from dotenv import load_dotenv
load_dotenv()
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

lucas = {"mail": "lukitas@gmail.com",
         "password": password,
         "phone_number": "+5493446570174",
         "name": "lucas",
         "lastname": "martinez",
         "age": "20",}
pepe = {"mail": "pepon@gmail.com",
        "password": password,
        "phone_number": "+5493446570174",
        "name": "lucas",
        "lastname": "martinez",
        "age": "20",}
juan = {"mail": "juan@gmail.com",
        "password": password,
        "phone_number": "+5493446570174",
        "name": "lucas",
        "lastname": "martinez",
        "age": "20",}

@pytest.fixture()
def twilio_mock(monkeypatch):
    client_twilio_mock = mock.Mock()
    monkeypatch.setattr("app.config.twilio.client_twilio", client_twilio_mock)
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
        "role": UserRoles.ATLETA.value,
        "name": lucas['name'],
        "lastname": lucas['lastname'],
        "age": lucas['age'],
    }

    response = client.post("/signup/", json=credentials)
    assert response.status_code == 201


def test_fail_if_user_already_exists(mongo_mock):
    credentials = {
        "mail": juan['mail'],
        "password": password,
        "phone_number": juan['phone_number'],
        "role": UserRoles.ATLETA.value,
        "name": juan['name'],
        "lastname": juan['lastname'],
        "age": juan['age'],
    }

    response = client.post("/signup/", json=credentials)
    assert response.status_code == 409
    

def test_check_validation_code(mongo_mock, twilio_mock):
    client.post("signup/validate_code?phone_number=%2B54333676862&verification_code=11111/")
    twilio_mock.verify.v2.services.return_value.verification_checks.create.assert_called_once()
