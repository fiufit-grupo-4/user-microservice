# import mongomock
# import pytest
# from fastapi.testclient import TestClient
# from app.main import app, logger
# from app.domain.UserRoles import UserRoles
#
# # TEST
# client = TestClient(app)
# lastname = 'titititi'
# encrypted_password = '$2b$12$T3HXmxRONP1sjTkk3Pqaq.9IYl5KNRhMHyJC4QxZPx0AqJpctDqeO'
#
# lucas = {"name": "lucas", "lastname": "martinez", "age": "20", "mail": "lukitas@gmail.com",
#          "encrypted_password": encrypted_password, "image": "lucas.png", 'blocked': False, 'role': UserRoles.ADMIN.value}
#
#
# # Mock MongoDB
# @pytest.fixture()
# def mongo_mock(monkeypatch):
#     mongo_client = mongomock.MongoClient()
#     db = mongo_client.get_database("user_microservice")
#     col = db.get_collection("users")
#     col.insert_one(lucas)
#
#     app.database = db
#     app.logger = logger
#     monkeypatch.setattr(app, "database", db)
#
#
# def test_get_me_success(mongo_mock):
#     login_response = client.post("/login/")
#
#     response = client.get("/me")
#     assert response.status_code == 200
#     assert response.json() == {
#         "name": "John",
#         "lastname": "Doe",
#         "age": 30,
#         "mail": "john.doe@example.com",
#         "image": "john.jpg",
#         "role": UserRoles.ADMIN.value,
#         "blocked": False,
#     }
#
#
# def test_get_me_not_found(mongo_mock):
#
#     response = client.get("/me")
#     assert response.status_code == 404
#     assert response.json() == {"detail": "User mock_user_id not found to get"}
#
#
# def test_get_me_unauthorized(mongo_mock):
#     response = client.get("/me")
#     assert response.status_code == 401
#     assert response.json() == {"detail": "Invalid credentials"}
