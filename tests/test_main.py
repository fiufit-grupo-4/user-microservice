import mongomock
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.main import logger

# TEST
client = TestClient(app)
lastname = 'titititi'
encrypted_password = '$2b$12$T3HXmxRONP1sjTkk3Pqaq.9IYl5KNRhMHyJC4QxZPx0AqJpctDqeO'

lucas = {"name": "lucas", "lastname": "martinez", "age": "20", "mail": "lukitas@gmail.com",
         "encrypted_password": encrypted_password}


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


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}


def test_get_all_users(mongo_mock):
    response = client.get("/users")
    assert response.status_code == 200
    res = response.json()
    for item in res:
        item.pop("id")
    assert all(item in res for item in [
        {"name": "lucas", "lastname": "martinez", "age": "20", "mail": "lukitas@gmail.com"}])


def test_modify_user(mongo_mock):
    credentials = {
        "mail": lucas['mail'],
        "password": lastname
    }
    response = client.put("/users/lukitas@gmail.com", json=credentials)
    assert response.status_code == 200
    assert response.json() == "User lukitas@gmail.com updated successfully"


def test_modify_user_error(mongo_mock):
    credentials = {
        "mail": "sofia@gmail.com",
        "password": lastname
    }
    response = client.put("/users/sofia@gmail.com", json=credentials)
    assert response.status_code == 404
    assert response.json() == "User sofia@gmail.com not found"


def test_delete_user(mongo_mock):
    credentials = {
        "mail": lucas['mail'],
        "password": lastname
    }
    response = client.delete("/users/lukitas@gmail.com", json=credentials)
    assert response.status_code == 200
    assert response.json() == "User lukitas@gmail.com deleted successfully"


def test_delete_user_error(mongo_mock):
    credentials = {
        "mail": "sofia@gmail.com",
        "password": lastname
    }
    response = client.delete("/users/sofia@gmail.com", json=credentials)
    assert response.status_code == 404
    assert response.json() == "User sofia@gmail.com not found"
