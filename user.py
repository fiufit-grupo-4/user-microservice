
class User(object):
    def __init__(self, name, lastname, age, mail, password):
        self.name = name
        self.last_name = lastname
        self.age = age
        self.mail = mail
        self.password = password
        # self.profile = Profile()

    def getName(self,):
        return self.name + ' ' + self.last_name

    def getAge(self):
        return self.age


"""
class Profile(object): 
    
    def __init__(self,name,age):
        self.name = name
        self.age = age
        
    def get_age(self):
        return self.age
    
    def get_name(self):
        return self.name
"""
