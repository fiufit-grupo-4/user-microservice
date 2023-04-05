import unittest
from starlette.testclient import TestClient
from app.main import app

class TestE2EUser(unittest.TestCase):
    def test_create_user(self):
        with TestClient(app) as client:
            response = client.post(
                "/users/",
                json={
                    "name": "Foo Bar",
                    "lastname": "pepe",
                    "mail": "ff@gmail.com",
                    "age": "20"
                },
            )
            assert response.status_code == 201
            res = response.json()
            res.pop("_id")
            assert res == {
                "name": "Foo Bar",
                "lastname": "pepe",
                "age": "20",
                "mail": "ff@gmail.com"
            }