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


def test_delete_user(mongo_mock):
    print("hola")
    id_lucas = client.get("/users/").json()[0].get('id')
    response = client.delete(f"/users/{id_lucas}")
    assert response.status_code == 200
    assert response.json() == f"User {id_lucas} deleted successfully"


def test_delete_user_error(mongo_mock):
    response = client.delete("/users/644234298a2a9d5f3db8f511")
    assert response.status_code == 404
    assert response.json() == "User 644234298a2a9d5f3db8f511 not found to delete"

