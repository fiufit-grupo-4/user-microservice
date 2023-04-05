from fastapi.testclient import TestClient
from app.main import app
from app.user.user import *
import json

'''
users["foo"] = User("Lucas", "Waisten", "20", "ss@gmail.com")
users["bar"] = User("Juana", "Waisten", "21", "xx@gmail.com")

# TEST
client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}

def test_create_user():
    response = client.post(
        "/users",
        json = {
                "name": "Foo Bar",
                "lastname": "pepe",
                "mail": "ff@gmail.com",
                "age": "20"
                },
    )
    assert response.status_code == 201
    res = response.json()
    res.pop("user_id")
    assert res == {
                    "name": "Foo Bar",
                    "lastname": "pepe",
                    "age": "20",
                    "mail": "ff@gmail.com"
                    }


def test_create_existing_user_error():
    response = client.post(
        "/users",
        json = {
                "user_id": "foo",
                "name": "Lucas", 
                "lastname": "Waisten",
                "age": "20",
                "mail": "ss@gmail.com"
                },
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
    # TODO: users["foo"] and users["bar"] will not be the only elements
    # at this point if any other test added users... time to mock! 
    response = client.get("/users")
    assert response.status_code == 200

    expected = [
        {'age': '20',
         'user_id': 'foo',
         'lastname': 'Waisten',
         'mail': 'ss@gmail.com',
         'name': 'Lucas'},
        {'age': '21',
         'user_id': 'bar',
         'lastname': 'Waisten',
         'mail': 'xx@gmail.com',
         'name': 'Juana'},
        {'name': 'Foo Bar',
         'lastname': 'pepe',
         'age': '20',
         'mail': 'ff@gmail.com'}
    ]

    assert len(expected) == len(response.json())

    jsonResponse = response.json()

    # TODO: this is a temporary fix, as response elements have real user ids
    # and testing ones do not. The db should be mocked soon...
    for i in range(len(jsonResponse)):
        jsonResponse[i].pop("user_id", None)
    for i in range(len(expected)):
        expected[i].pop("user_id", None)
    ########################################################################
    for e in expected:
        assert e in jsonResponse


def test_get_user_by_mail():
    response = client.get("/users?mail_filter=ss@gmail.com")
    assert response.status_code == 200
    assert response.json() == [{'age': '20',
                              'user_id': 'foo',
                              'lastname': 'Waisten',
                              'mail': 'ss@gmail.com',
                              'name': 'Lucas'}]


def test_get_user_by_wrong_mail():
    response = client.get("/users?mail_filter=sx@gmail.com")

    assert response.status_code == 200
    assert response.json() == []

'''
"""
def test_patch_user_mail():
    request_body = {"mail" : "latylam@gmail.com"}
    response = client.patch("/users/foo?update_user_request=latylam@gmail.com")
    assert response.status_code == 200
    assert response.json() == {
            "user_id": "foo",
            "name": "Lucas",
            "lastname": "Waisten",
            "age": "20",
            "mail": "ss@gmail.com",
    }
"""
