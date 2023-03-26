class User(object):
    def __init__(self, profile):
        self.profile = profile
        #self.last_name = lastname
        # self.age = age
        # self.mail = mail
        # self.password = password
        # self.profile = Profile()
    
    def getAge(self):
        return self.profile.get_age()
    def getName(self):
        return self.profile.get_name()

class Profile(object): 
    def __init__(self,name,age):
        self.name = name
        self.age = age
    def get_age(self):
        return self.age
    def get_name(self):
        return self.name
