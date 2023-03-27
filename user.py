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
        self.usuarios_seguidos = []
        self.seguidores = []

    def getName(self, ):
        return self.name + ' ' + self.last_name

    def getAge(self):
        return self.age

    def seguir_usuairio(self, usuario):
        self.usuarios_seguidos.append(usuario)

    def dejar_seguir_usuario(self, usuario):
        self.usuarios_seguidos.remove(usuario)

    def usuarios_seguidos(self):
        return self.usuarios_seguidos

    def seguidores(self):
        return self.seguidores


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

    def listar_metas(self):
        return [meta.titulo for meta in self.metas]

    def visualizar_meta(self, meta):
        return meta.visualizar()

    def meta_cumplida(self, meta):
        meta.cumplida()





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
