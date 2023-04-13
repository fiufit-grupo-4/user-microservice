from fastapi.testclient import TestClient
import mongomock
import pytest
from app.main import app

# TEST
client = TestClient(app)
password = 'titititi'
encrypted_password = '$2b$12$T3HXmxRONP1sjTkk3Pqaq.9IYl5KNRhMHyJC4QxZPx0AqJpctDqeO'

lucas = {"mail": "lukitas@gmail.com", "password": "titititi"}
juan = {"name": "juan", "lastname": "ruiz", "age": "20", "mail": "juan@gmail.com",
         "encrypted_password": encrypted_password, "session_token": "token"}


# Mock MongoDB
@pytest.fixture()
def mongo_mock(monkeypatch):
    mongo_client = mongomock.MongoClient()
    db = mongo_client.get_database("user_microservice")
    col = db.get_collection("users")


    app.database = db
    monkeypatch.setattr(app, "database", db)

def testUserLucasSingUpStatus200(mongo_mock):
    credentials = {
        "mail": lucas['mail'],
        "password": password
    }

    response = client.post("/signup/", json=credentials) # cambia la URL del endpoint aquí
    print(response)
    assert response.status_code == 200