import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import mongomock
import pytest
from app.main import app

# TEST
client = TestClient(app)

# Mock MongoDB
@pytest.fixture()
def mongo_mock(monkeypatch):
    client = mongomock.MongoClient()
    db = client.get_database("user_microservice")
    col = db.get_collection("users")

    person_1 = {"name": "lucas", "lastname": "pepe", "age": "20", "mail": "pepe@gmail.com"}
    col.insert_one(person_1).inserted_id

    app.database = db
    monkeypatch.setattr(app, "database", db)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}


def test_create_user(mongo_mock):
    user = {
            "name": "Foo Bar",
            "lastname": "pepe",
            "age": "20",
            "mail": "ff@gmail.com"
        }

    response = client.post("/users/", json=user)
    assert response.status_code == 201

    res = response.json()
    res.pop("_id")
    assert res == user

    response = client.get("/users/")
    res = response.json()
    for item in res:
        item.pop("_id")

    assert user in res


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


# def test_get_all_users_by_mail_without_mail():
#     # TODO: users["foo"] and users["bar"] will not be the only elements
#     # at this point if any other test added users... time to mock!
#     response = client.get("/users")
#     assert response.status_code == 200

#     expected = [
#         {'age': '20',
#          'user_id': 'foo',
#          'lastname': 'Waisten',
#          'mail': 'ss@gmail.com',
#          'name': 'Lucas'},
#         {'age': '21',
#          'user_id': 'bar',
#          'lastname': 'Waisten',
#          'mail': 'xx@gmail.com',
#          'name': 'Juana'},
#         {'name': 'Foo Bar',
#          'lastname': 'pepe',
#          'age': '20',
#          'mail': 'ff@gmail.com'}
#     ]

#     assert len(expected) == len(response.json())

#     jsonResponse = response.json()

#     # TODO: this is a temporary fix, as response elements have real user ids
#     # and testing ones do not. The db should be mocked soon...
#     for i in range(len(jsonResponse)):
#         jsonResponse[i].pop("user_id", None)
#     for i in range(len(expected)):
#         expected[i].pop("user_id", None)
#     ########################################################################
#     for e in expected:
#         assert e in jsonResponse


# def test_get_user_by_mail():
#     response = client.get("/users?mail_filter=ss@gmail.com")
#     assert response.status_code == 200
#     assert response.json() == [{'age': '20',
#                                 'user_id': 'foo',
#                                 'lastname': 'Waisten',
#                                 'mail': 'ss@gmail.com',
#                                 'name': 'Lucas'}]


# def test_get_user_by_wrong_mail():
#     response = client.get("/users?mail_filter=sx@gmail.com")

#     assert response.status_code == 200
#     assert response.json() == []


# def test_patch_user_mail():
#     response = client.patch("/users/foo?update_user_request=latylam@gmail.com")
#     assert response.status_code == 200
#     assert response.json() == {
#         "user_id": "foo",
#         "name": "Lucas",
#         "lastname": "Waisten",
#         "age": "20",
#         "mail": "ss@gmail.com",
#     }
