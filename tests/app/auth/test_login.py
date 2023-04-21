from fastapi.testclient import TestClient
import mongomock
import pytest
from app.main import app
from app.main import logger

# TEST
client = TestClient(app)
password = 'titititi'
encrypted_password = '$2b$12$T3HXmxRONP1sjTkk3Pqaq.9IYl5KNRhMHyJC4QxZPx0AqJpctDqeO'

lucas = {"name": "lucas", "lastname": "martinez", "age": "20", "mail": "lukitas@gmail.com",
         "encrypted_password": encrypted_password, "session_token": "token"}
juan = {"name": "juan", "lastname": "ruiz", "age": "20", "mail": "juan@gmail.com",
        "encrypted_password": encrypted_password, "session_token": "token"}


# Mock MongoDB
@pytest.fixture()
def mongo_mock(monkeypatch):
    mongo_client = mongomock.MongoClient()
    db = mongo_client.get_database("user_microservice")
    col = db.get_collection("users")
    col.insert_one(lucas)
    col.insert_one(juan)

    app.database = db
    app.logger = logger
    monkeypatch.setattr(app, "database", db)


def testUserLucasLoginStatus200(mongo_mock):
    credentials = {
        "mail": lucas['mail'],
        "password": password
    }

    response = client.post("/login/", json=credentials)
    print(response)
    assert response.status_code == 200


def testUserJuanLoginStatus200(mongo_mock):
    credentials = {
        "mail": juan['mail'],
        "password": password
    }

    response = client.post("/login/", json=credentials)
    print(response)
    assert response.status_code == 200


def testUserUnregisteredLoginStatus401(mongo_mock):
    credentials = {
        "mail": "andy@gmail.com",
        "password": password
    }

    response = client.post("/login/", json=credentials)
    print(response)
    assert response.status_code == 401
    

def testOtherUserUnregisteredLoginStatus401(mongo_mock):
    credentials = {
        "mail": "mabel@gmail.com",
        "password": password
    }

    response = client.post("/login/", json=credentials)
    print(response)
    assert response.status_code == 401
