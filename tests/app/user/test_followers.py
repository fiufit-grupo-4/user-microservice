from dotenv import load_dotenv
load_dotenv()
import pytest
import mongomock
from fastapi.testclient import TestClient
from app.main import app
from app.main import logger
from app.config.auth_settings import SettingsAuth

client = TestClient(app)
lucas = {
    "name": "lucas",
    "lastname": "martinez",
    "age": "20",
    "mail": "lukitas@gmail.com",
    "encrypted_password": "encrypted_password",
    "image": "lucas.png",
    'blocked': False,
    'phone_number': '+5493446570174',
    'trainings': [],
    'following': [],
    'followers': [],
    'device_token': None,
}

juan = {
    "name": "juan",
    "lastname": "perez",
    "age": "20",
    "mail": "pepe@gmail.com",
    "encrypted_password": "encrypted_password",
    "image": "pepe.png",
    'blocked': False,
    'phone_number': '+5493446578175',
    'trainings': [],
    'following': [],
    'followers': [],
    'device_token': None,
}


@pytest.fixture()
def mongo_mock(monkeypatch):
    mongo_client = mongomock.MongoClient()
    db = mongo_client.get_database("user_microservice")
    col = db.get_collection("users")
    col.insert_many([lucas, juan])
    app.database = db
    app.logger = logger
    monkeypatch.setattr(app, "database", db)


def test_follow_user(mongo_mock):
    id_lucas = client.get("/users/").json()[0].get('id')
    access_token_lucas = SettingsAuth.generate_token(id_lucas)
    id_juan = client.get("/users/").json()[1].get('id')

    response = client.post(f"/users/{id_juan}/follow", headers={"Authorization": f"Bearer {access_token_lucas}"})
    print(response)
    lucas_following = client.get(f"/users/{id_lucas}").json().get('following')
    juan_followers = client.get(f"/users/{id_juan}").json().get('followers')

    assert response.status_code == 200
    assert juan_followers == [id_lucas]
    assert lucas_following == [id_juan]


def test_unfollow_user(mongo_mock):
    id_lucas = client.get("/users/").json()[0].get('id')
    id_juan = client.get("/users/").json()[1].get('id')
    access_token_juan = SettingsAuth.generate_token(id_juan)
    client.post(f"/users/{id_lucas}/follow", headers={"Authorization": f"Bearer {access_token_juan}"})

    response = client.post(f"/users/{id_lucas}/unfollow", headers={"Authorization": f"Bearer {access_token_juan}"})
    juan_following = client.get(f"/users/{id_juan}").json().get('following')
    lucas_followers = client.get(f"/users/{id_lucas}").json().get('followers')

    assert response.status_code == 200
    assert juan_following == []
    assert lucas_followers == []

