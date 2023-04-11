from typing import Optional
from pydantic import BaseModel, EmailStr


def create_user(name: str, lastname: str, mail: str, age: str):
    new_user = User(name=name, lastname=lastname, mail=mail, age=age)
    return new_user


class UserRequest(BaseModel):
    name: str
    lastname: str
    mail: Optional[EmailStr]
    age: str


class UserResponse:
    def __init__(self, user_id, name, lastname, age, mail):
        self._id = user_id
        self.name = name
        self.lastname = lastname
        self.age = age
        self.mail = mail

    class Config:
        orm_mode = True


class UpdateUserRequest(BaseModel):
    mail: EmailStr


class User:
    def __init__(self, name, lastname, age, mail):
        self.name = name
        self.lastname = lastname
        self.age = age
        self.mail = mail
        self.session_token = None
        self.encrypted_password = None

    def create_session(self, token_generator): self.session_token = token_generator.generate_session_token()
