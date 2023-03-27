from Metricas import *
from Metas import *

class User:
    def __init__(self, name, lastname, age, mail, password):
        self.name = name
        self.last_name = lastname
        self.age = age
        self.mail = mail
        self.password = password
        self.training = []
        self.usuarios_seguidos = 0

    def getName(self, ):
        return self.name + ' ' + self.last_name

    def getAge(self):
        return self.age


class Trainer(User):
    def __init__(self, name, lastname, age, mail, password):
        super().__init__(name, lastname, age, mail, password)
        self.entrenamientos = []
        self.certificado_entrenador_reconocido = False

    def creacion_entrenamiento(self):
        pass

    def edicion_plan_entrenamiento(self):
        pass

    def get_listado_entrenamiento(self):
        return self.entrenamientos


class Athlete(User):
    def __init__(self, name, lastname, age, mail, password):
        super().__init__(name, lastname, age, mail, password)
        self.metricas = Metricas()
        self.metas = []

    def actualizar_metricas(self, distancia, tiempo, calorias, hitos, actividad):
        self.metricas.actualizar(distancia, tiempo, calorias, hitos, actividad)

    def crear_meta(self,  titulo, descripcion, metrica, limite_tiempo=False):
        self.metas.append(Meta(titulo, descripcion, metrica, limite_tiempo))

    def actualizar_meta(self, meta, titulo, descripcion, metrica, limite_tiempo=False):
        meta.actualizar(titulo, descripcion, metrica, limite_tiempo)

    def eliminar_meta(self, meta):
        self.metas.remove(meta)

# Tema perfil, se puede no hacer

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
