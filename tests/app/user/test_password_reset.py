import mongomock
import pytest
from twilio.base.exceptions import TwilioRestException
from fastapi.testclient import TestClient
from app.main import app
from app.main import logger

# TEST
client = TestClient(app)
email = "waistenlucas@gmail.com"
validation_code = "123456"
new_password = "new_password"
lastname = 'titititi'
encrypted_password = '$2b$12$T3HXmxRONP1sjTkk3Pqaq.9IYl5KNRhMHyJC4QxZPx0AqJpctDqeO'
lucas = {
    "name": "lucas",
    "lastname": "martinez",
    "age": "20",
    "mail": email,
    "encrypted_password": encrypted_password,
    "image": "lucas.png",
    'blocked': False
}

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

# Mock Twilio
@pytest.fixture()
def twilio_mock(monkeypatch):
    class MockVerificationChecks:
        def create(self, to, code):
            if code == validation_code:
                return
            else:
                raise TwilioRestException()

    class MockVerifications:
        def __getattr__(self, attr):
            return MockVerificationChecks()

    class MockVerify:
        def __getattr__(self, attr):
            return MockVerifications()

    class MockServices:
        def __call__(self, *args, **kwargs):
            return MockVerify()

    monkeypatch.setattr("app.auth.password_reset.client_twilio.verify.v2.services", MockServices())



def test_forgot_password(mongo_mock, twilio_mock):
    credentials = {
        "mail": email
    }
    response = client.post("/login/forgot_password", json=credentials)
    assert response.status_code == 200
    assert response.json() == {"detail": "Password reset link sent"}

def test_forgot_password_user_not_found():
    response = client.post("/login/forgot_password", json={"mail": "nonexistent@example.com"})
    assert response.status_code == 404
    assert response.json() == "User not found"

def test_reset_password(mongo_mock, twilio_mock):
    response = client.post(f"/login/reset_password/{validation_code}", json={"mail": email, "new_password": new_password})
    assert response.status_code == 200
    assert response.json() == {"detail": "Password reset successfully"}

def test_reset_password_invalid_validation_code():
    response = client.post("/login/reset_password/invalid_code", json={"mail": email, "new_password": new_password})
    assert response.status_code == 400
    assert response.json() == "Invalid verification code or email"

def test_reset_password_user_not_found():
    response = client.post(f"/login/reset_password/{validation_code}", json={"mail": "nonexistent@example.com", "new_password": new_password})
    assert response.status_code == 404
    assert response.json() == "User not found, email not registered"
