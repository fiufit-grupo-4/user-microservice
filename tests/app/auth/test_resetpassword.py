from unittest import mock
from fastapi.testclient import TestClient
import mongomock
import pytest
from os import environ as env
from app.main import app
from app.main import logger

# TEST
client = TestClient(app)

password = 'titititi'
lucas = {"mail": "lukitas@gmail.com", "password": password, "phone_number": "+5493446570174"}
pepe = {"mail": "pepon@gmail.com", "password": password, "phone_number": "+5493446570174"}
juan = {"mail": "juan@gmail.com", "password": password, "phone_number": "+5493446570174"}


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


@pytest.fixture()
def twilio_mock(monkeypatch):
    client_twilio_mock = mock.Mock()
    monkeypatch.setattr("app.settings.twilio.client_twilio", client_twilio_mock)
    return client_twilio_mock


def test_forgot_password_user_not_found(mongo_mock, twilio_mock):
    credentials = {
        "mail": "unknown@example.com"
    }

    response = client.post("/login/forgot_password", json=credentials)
    assert response.status_code == 404
    assert response.json() == "User not found"


def test_forgot_password_success(mongo_mock, twilio_mock):
    credentials = {
        "mail": juan['mail']
    }

    response = client.post("/login/forgot_password", json=credentials)
    assert response.status_code == 200
    assert response.json() == {"detail": "Password reset link sent"}

    # Verificar que se haya llamado a la función de envío de correo electrónico de Twilio
    twilio_mock.verify.v2.services.return_value.verifications.create.assert_called_once_with(
        channel_configuration={
            'template_id': env.get('SENGRID_EMAIL_TEMPLATE_ID'),
            'from': 'lwaisten@fi.uba.ar',
            'from_name': 'Lucas Waisten',
        },
        to=juan['mail'],
        channel='email',
    )


def test_reset_password_success(mongo_mock, twilio_mock):
    verification_checks_mock = mock.Mock()
    twilio_mock.verify.v2.services.return_value.verification_checks.create.return_value = verification_checks_mock

    credentials = {
        "mail": juan['mail'],
        "new_password": '1234'
    }
    validation_code = "123456"

    response = client.post(f"/login/reset_password/{validation_code}", json=credentials)
    assert response.status_code == 200
    assert response.json() == {"detail": "Password reset successfully"}

    user = app.database["users"].find_one({"mail": juan['mail']})
    assert user['encrypted_password'] is not None

    twilio_mock.verify.v2.services.return_value.verification_checks.create.assert_called_once_with(
        to=juan['mail'], code=validation_code
    )


def test_reset_password_user_not_found(mongo_mock, twilio_mock):
    credentials = {
        "mail": "unknown@example.com",
        "new_password": "newpassword"
    }
    validation_code = "123456"

    response = client.post(f"/login/reset_password/{validation_code}", json=credentials)
    assert response.status_code == 404
    assert response.json() == "User not found, email not registred"
