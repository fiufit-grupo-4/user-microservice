from fastapi.testclient import TestClient
from main import app, users
from user import *

users["foo"] = User("foo", "Lucas", "Waisten", "20", "ss@gmail.com")
users["bar"] = User("bar", "Juana", "Waisten", "21", "xx@gmail.com")


# TEST
client = TestClient(app)


def test_create_user():
    response = client.post(
        "/users/",
        json={
              "name": "Foo Bar",
              "lastname": "pepe",
              "age": "20",
              "mail": "ff@gmail.com"},
    )
    assert response.status_code == 201
    res = response.json()
    res.pop("user_id")
    assert res =={
                               "name": "Foo Bar",
                               "lastname": "pepe",
                               "age": "20",
                               "mail": "ff@gmail.com"}


def test_create_existing_user_error():
    response = client.post(
        "/users/",
        json={"user_id": "foo", "name": "Lucas",  "lastname": "Waisten", "age": "20","mail": "ss@gmail.com"},
    )

    assert response.status_code == 400
    assert response.json() == "User Lucas already exists"


def test_get_user_by_user_id():
    response = client.get("/users/foo")
    assert response.status_code == 200
    assert response.json() == {
        "user_id": "foo",
        "name": "Lucas",
        "lastname": "Waisten",
        "age": "20",
        "mail": "ss@gmail.com",
    }


def test_get_all_users_by_mail_without_mail():
    response = client.get("/users")
    assert response.status_code == 200

    assert response.json() == [{'age': '20',
                              'user_id': 'foo',
                              'lastname': 'Waisten',
                              'mail': 'ss@gmail.com',
                              'name': 'Lucas'},
                               {'age': '21',
                              'user_id': 'bar',
                              'lastname': 'Waisten',
                              'mail': 'xx@gmail.com',
                              'name': 'Juana'}]


def test_get_user_by_mail():
    response = client.get("/users?mail_filter=ss@gmail.com")
    assert response.status_code == 200
    assert response.json() == [{'age': '20',
                              'user_id': 'foo',
                              'lastname': 'Waisten',
                              'mail': 'ss@gmail.com',
                              'name': 'Lucas'}]
