from fastapi.testclient import TestClient
import mongomock
import pytest

from app.domain.UserRoles import UserRoles
from app.main import app
from app.main import logger

# TEST
client = TestClient(app)
password = 'titititi'

lucas = {"mail": "lukitas@gmail.com", "password": password}
pepe = {"mail": "pepon@gmail.com", "password": password}
juan = {"mail": "juan@gmail.com", "password": password}


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
        "role": UserRoles.ATLETA.value
    }

    response = client.post("/signup/", json=credentials)
    assert response.status_code == 201


def test_fail_if_user_already_exists(mongo_mock):
    credentials = {
        "mail": juan['mail'],
        "password": password,
        "role": UserRoles.ATLETA.value
    }

    response = client.post("/signup/", json=credentials)
    assert response.status_code == 409
