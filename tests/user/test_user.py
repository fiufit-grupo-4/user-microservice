import unittest
from app.user.user import *


class TestUser(unittest.TestCase):

    def test_createUser(self):
        user = User('Juan', 'Perez', '25', 'juancitoperez@gmail.com')
        self.assertEqual(type(user), User, 'Deberia ser un objeto de tipo User')

    def test_userName(self):
        user = User('Juan', 'Perez', '25', 'juancitoperez@gmail.com')
        self.assertEqual(user.name, 'Juan', 'El nombre deberia ser: Juan')

    def test_userAge(self):
        user = User('Juan', 'Perez', '25', 'juancitoperez@gmail.com')
        self.assertEqual(user.age, '25', 'La edad deberia ser: 25')


if __name__ == '__main__':
    unittest.main()
