from typing import List, Optional
from fastapi import status
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse
from main import UserResponse, app

fake_db = {
    "foo": {"id": "foo", "name": "Lucas", "lastname": "Waisten", "age": "20", "mail": "ss@gmail.com"},
    "bar": {"id": "bar", "name": "Juana", "lastname": "Waisten", "age": "20", "mail": "xx@gmail.com"},
}

@app.get("/users/{user_id}", response_model=UserResponse,status_code=status.HTTP_200_OK)
async def read_main(user_id: str):

    if user_id not in fake_db:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=f'User {user_id} not found',)
    return fake_db[user_id]

@app.get('/users', response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(mail_filter: Optional[str] = None):
    users_filtered = []
    for user_id, user in fake_db.items():
        if mail_filter:
            if mail_filter in user['mail']:
                users_filtered.append(user)
        else:
            users_filtered.append(user)
    return users_filtered

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserResponse):
    if user.id in fake_db:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content=f'User {user.name} already exists', )
    fake_db[user.id] = user
    return user

# TEST
client = TestClient(app)

def test_read_user():
    response = client.get("/users/foo")
    assert response.status_code == 200
    assert response.json() == {
        "id": "foo",
        "name": "Lucas",
        "lastname": "Waisten",
        "age": "20",
        "mail": "ss@gmail.com",
    }

def test_create_user():
    response = client.post(
        "/users/",
        json={"id": "foobar",
              "name": "Foo Bar",
              "lastname": "pepe",
              "age": "20",
              "mail": "ff@gmail.com"},
    )
    assert response.status_code == 201
    assert response.json() == {"id": "foobar",
                               "name": "Foo Bar",
                               "lastname": "pepe",
                               "age": "20",
                               "mail": "ff@gmail.com"}

def test_create_existing_user():
    response = client.post(
        "/users/",
        json={"id": "foo", "name": "Lucas",  "lastname": "Waisten", "age": "20","mail": "ss@gmail.com"},
    )
    assert response.status_code == 400
    assert response.json() == "User Lucas already exists"

def test_getAUserWithMail():
    response = client.get("/users") # "email_filter=ss@gmail.com")
    assert response.status_code == 200
    assert response.json() == [{'age': '20',
                              'id': 'foo',
                              'lastname': 'Waisten',
                              'mail': 'ss@gmail.com',
                              'name': 'Lucas'},
                               {'age': '20',
                              'id': 'bar',
                              'lastname': 'Waisten',
                              'mail': 'xx@gmail.com',
                              'name': 'Juana'}]

def test_getAUserWithMail():
    response = client.get("/users?mail_filter=ss@gmail.com")
    assert response.status_code == 200
    assert response.json() == [{'age': '20',
                              'id': 'foo',
                              'lastname': 'Waisten',
                              'mail': 'ss@gmail.com',
                              'name': 'Lucas'}]