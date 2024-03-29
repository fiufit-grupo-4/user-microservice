from dotenv import load_dotenv
load_dotenv()
import mongomock
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app, logger
# TEST
client = TestClient(app)

encrypted_password = '$2b$12$T3HXmxRONP1sjTkk3Pqaq.9IYl5KNRhMHyJC4QxZPx0AqJpctDqeO'
# Mock users
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


def test_get_users(mongo_mock):
    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    user = response.json()[0]
    assert user["name"] == lucas["name"]
    assert user["lastname"] == lucas["lastname"]
    assert user["age"] == lucas["age"]
    assert user["mail"] == lucas["mail"]
    assert user["image"] == lucas["image"]
    assert user["blocked"] == lucas["blocked"]
    assert "id" in user
