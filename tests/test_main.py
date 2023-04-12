import unittest
from fastapi import FastAPI
from fastapi.security import HTTPBasicCredentials
from fastapi.testclient import TestClient
import mongomock
import pytest
from app.main import app

# TEST
client = TestClient(app)
password = 'titititi'
encrypted_password = '$2b$12$T3HXmxRONP1sjTkk3Pqaq.9IYl5KNRhMHyJC4QxZPx0AqJpctDqeO'

lucas = {"name": "lucas", "lastname": "martinez", "age": "20", "mail": "lukitas@gmail.com",
         "encrypted_password": encrypted_password, "session_token": "token"}


# Mock MongoDB
@pytest.fixture()
def mongo_mock(monkeypatch):
    mongo_client = mongomock.MongoClient()
    db = mongo_client.get_database("user_microservice")
    col = db.get_collection("users")
    col.insert_one(lucas)

    app.database = db
    monkeypatch.setattr(app, "database", db)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}


def test_login(mongo_mock):
    credentials = {
        "username": lucas['mail'],
        "password": password
    }

    response = client.post("/login/", json=credentials)
    print(response)
    assert response.status_code == 200


"""
def test_get_all_users(mongo_mock):
    response = client.get("/users/")
    assert response.status_code == 200
    res = response.json()
    for item in res:
        item.pop("_id")
    assert all(item in res for item in [
        {"name": "lucas", "lastname": "pepe", "age": "20", "mail": "pepe@gmail.com"}])


def test_create_existing_user_error():
    user = {
        "name": "lucas",
        "lastname": "pepe",
        "age": "20",
        "mail": "pepe@gmail.com"
    }

    client.post("/users/", json=user)

    response = client.post("/users/", json=user)

    assert response.status_code == 400
    assert response.json() == "User pepe@gmail.com already exists"
"""
