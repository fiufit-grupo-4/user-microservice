import unittest
from app.user.user import *


class TestUser(unittest.TestCase):

    def test_createUser(self):
        user = User('juan@gmail.com', 'passw0rd')
        self.assertEqual(type(user), User, 'Deberia ser un objeto de tipo User')

    def test_userAttributes(self):
        user = User('juan@gmail.com', 'passw0rd', 'Juan', 'Perez', 25)
        self.assertEqual(user.name, 'Juan')
        self.assertEqual(user.lastname, 'Perez')
        self.assertEqual(user.age, 25)


if __name__ == '__main__':
    unittest.main()
