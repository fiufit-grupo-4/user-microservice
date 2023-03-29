from fastapi.testclient import TestClient
from main import *
from fastapi import status
from typing import List, Optional
from starlette.responses import JSONResponse



client = TestClient(app)

fake_secret_token = "coneofsilence"

fake_db = {
    "1": {"user_id": "1", "name": "Lucas", "lastname": "Waisten", "mail": "ss@gmail.com", "age": "20"},
    "2": {"user_id": "2", "name": "Juana", "lastname": "Sota", "mail": "sotajuana@gmail.com", "age": "20"},
}


##################################
#####          Mock de la FastApi          #####
##################################


@app.post('/users', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_users(user_request: UserRequest):
    if not validate_username(user_request.name, fake_db):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content=f'User {user_request.name} already exists', )
    return create_user(user_request.name, user_request.lastname, user_request.mail, user_request.age, fake_db)


@app.get('/users', response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(email_filter: Optional[str] = None):
    users_filtered = []
    for user_id, user in fake_db.items():
        if email_filter:
            if email_filter in user.mail:
                users_filtered.append(user)
        else:
            users_filtered.append(user)
    return users_filtered


@app.get('/users/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(user_id: str):
    if user_id not in fake_db:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f'User {user_id} not found',)
    return fake_db[user_id]


def test_getAUserWithMail():
    response = client.get("/users?email_filter=ss@gmail.com")
    assert response.status_code == 200
    assert response.json() == {"user_id": "1", "name": "Lucas", "lastname": "Waisten", "mail": "ss@gmail.com",
                               "age": "20"}


def test_getEmptyListOfUsers():
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == []
