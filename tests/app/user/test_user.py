import unittest
from app.user.user import User


class TestUser(unittest.TestCase):

    def test_createUser(self):
        user = User(mail='juan@gmail.com',password= 'passw0rd',phone_number='+5493454651654',role=1)
        self.assertEqual(type(user), User, 'Deberia ser un objeto de tipo User')

    def test_userAttributes(self):
        user = User(mail='juan@gmail.com',password= 'passw0rd',phone_number='+5493454651654',role=1, name='Juan', lastname='Perez', age=25)
        self.assertEqual(user.name, 'Juan')
        self.assertEqual(user.lastname, 'Perez')
        self.assertEqual(user.age, 25)


if __name__ == '__main__':
    unittest.main()
