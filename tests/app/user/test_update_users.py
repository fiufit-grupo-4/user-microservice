from dotenv import load_dotenv
load_dotenv()
import mongomock
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.main import logger

client = TestClient(app)
lastname = 'titititi'
encrypted_password = '$2b$12$T3HXmxRONP1sjTkk3Pqaq.9IYl5KNRhMHyJC4QxZPx0AqJpctDqeO'

lucas = {
    "name": "lucas",
    "lastname": "martinez",
    "age": "20",
    "mail": "lukitas@gmail.com",
    "encrypted_password": encrypted_password,
    "image": "lucas.png",
    'blocked': False,
    'phone_number': '+5493446570174',
    'trainings': []
}

@pytest.fixture()
def mongo_mock(monkeypatch):
    mongo_client = mongomock.MongoClient()
    db = mongo_client.get_database("user_microservice")
    col = db.get_collection("users")
    col.insert_one(lucas)

    app.database = db
    app.logger = logger
    monkeypatch.setattr(app, "database", db)


def test_modify_user(mongo_mock):
    credentials = {
        "mail": lucas['mail'],
        "name": 'Juan',
        "age": '25'
    }
    id_lucas = client.get("/users/").json()[0].get('id')

    response = client.patch(f"/users/{id_lucas}", json=credentials)
    assert response.status_code == 200
    assert response.json() == f"User {id_lucas} updated successfully"

    lucas_update = client.get(f"/users/{id_lucas}").json()

    assert lucas_update["name"] == credentials["name"]
    assert lucas_update["lastname"] == lucas["lastname"]
    assert lucas_update["age"] == credentials["age"]
    assert lucas_update["mail"] == lucas["mail"]
    assert lucas_update["image"] == lucas["image"]
    assert lucas_update["blocked"] == lucas["blocked"]
    assert lucas_update["phone_number"] == lucas["phone_number"]


def test_modify_user_error(mongo_mock):
    credentials = {
        "mail": "sofia@gmail.com",
        "password": lastname
    }

    response = client.patch("/users/644234298a2a9d5f3db8f511", json=credentials)
    assert response.status_code == 404
    assert response.json() == "User 644234298a2a9d5f3db8f511 not found"

