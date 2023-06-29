from dotenv import load_dotenv
load_dotenv()
from bson import ObjectId
import mongomock
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.main import logger
from app.config.auth_settings import SettingsAuth
from requests.models import Response

# TEST
client = TestClient(app)
lastname = 'titititi'
encrypted_password = '$2b$12$T3HXmxRONP1sjTkk3Pqaq.9IYl5KNRhMHyJC4QxZPx0AqJpctDqeO'

lucas = {"name": "lucas", "lastname": "martinez", "age": "20", "mail": "lukitas@gmail.com",
         "encrypted_password": encrypted_password, "image": "lucas.png", 'blocked': False, 'trainings': []}

training_id_mock = str(ObjectId())
trainer_id_example_mock = "645dc49b047ac6322c28c231"

async def mock_get(*args, **kwargs):
    response = Response()
    response.status_code = 200
    response.json = lambda: {"id": training_id_mock, 
                             "id_trainer": trainer_id_example_mock,
                             "title": "A",
                             "description": "string",
                             "type": "Walking",
                             "difficulty": "Fácil"
                            }
    return response



# Mock MongoDB
@pytest.fixture()
def mongo_mock(monkeypatch):
    mongo_client = mongomock.MongoClient()
    db = mongo_client.get_database("user_microservice")
    col = db.get_collection("users")
    col.insert_one(lucas)

    app.database = db
    app.logger = logger
    monkeypatch.setattr(app, "database", db)

    monkeypatch.setattr("app.user.training_small.ServiceTrainers.get", mock_get)


def test_post_training(mongo_mock):
    # get id lucas
    id_lucas = client.get("/users/").json()[0].get('id')
    access_token_lucas = SettingsAuth.generate_token(id_lucas)
    
    response = client.post(f"/users/me/trainings/{training_id_mock}", headers={"Authorization": f"Bearer {access_token_lucas}"})
    assert response.status_code == 200
    assert response.json().get("id_training") == training_id_mock
    assert response.json().get("id_trainer") == trainer_id_example_mock
    assert response.json().get("title") == "A"
    assert response.json().get("type") == "Walking"
    assert response.json().get("difficulty") == "Fácil"
    
    response = client.get(f"/users/{id_lucas}")
    assert response.status_code == 200
    assert response.json().get("trainings")[0].get("id_training") == training_id_mock
    

# post dos veces del mismo trnainig no es posible
def test_post_training_two_times_retuns_409(mongo_mock):
    id_lucas = client.get("/users/").json()[0].get('id')
    access_token_lucas = SettingsAuth.generate_token(id_lucas)
    
    response = client.post(f"/users/me/trainings/{training_id_mock}", headers={"Authorization": f"Bearer {access_token_lucas}"})
    assert response.status_code == 200
    assert response.json().get("id_training") == training_id_mock
    assert response.json().get("id_trainer") == trainer_id_example_mock
    assert response.json().get("title") == "A"
    assert response.json().get("type") == "Walking"
    assert response.json().get("difficulty") == "Fácil"
    
    response = client.post(f"/users/me/trainings/{training_id_mock}", headers={"Authorization": f"Bearer {access_token_lucas}"})
    assert response.status_code == 409

def test_delete_training(mongo_mock):
    # get id lucas
    id_lucas = client.get("/users/").json()[0].get('id')
    access_token_lucas = SettingsAuth.generate_token(id_lucas)
    
    response = client.post(f"/users/me/trainings/{training_id_mock}", headers={"Authorization": f"Bearer {access_token_lucas}"})
    assert response.status_code == 200
    assert response.json().get("id_training") == training_id_mock
    assert response.json().get("id_trainer") == trainer_id_example_mock
    assert response.json().get("title") == "A"
    assert response.json().get("type") == "Walking"
    assert response.json().get("difficulty") == "Fácil"
    
    response = client.get(f"/users/{id_lucas}")
    assert response.status_code == 200
    assert response.json().get("trainings")[0].get("id_training") == training_id_mock
    
    response = client.delete(f"/users/me/trainings/{training_id_mock}", headers={"Authorization": f"Bearer {access_token_lucas}"})
    assert response.status_code == 200
    
    response = client.get(f"/users/{id_lucas}")
    assert response.status_code == 200
    assert response.json().get("trainings") == []