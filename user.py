from Metricas import *
from Metas import *
from PlanEntrenamiento import *


class User:
    def __init__(self, user_id, name, lastname, age, mail): # password=""):
        self.user_id = user_id
        self.name = name
        self.lastname = lastname
        self.mail = mail
        self.age = age
        '''
        self.password = password
        self.training = []
        self.usuarios_seguidos = []
        self.seguidores = []
        '''

    def getName(self):
        return self.name + ' ' + self.lastname

    def getAge(self):
        return self.age
    '''
    def seguir_usuairio(self, usuario):
        self.usuarios_seguidos.append(usuario)

    def dejar_seguir_usuario(self, usuario):
        self.usuarios_seguidos.remove(usuario)

    def usuarios_seguidos(self):
        return self.usuarios_seguidos

    def seguidores(self):
        return self.seguidores


def no_of_argu(*args):
    return len(args)


class Trainer(User):
    def __init__(self, name, lastname, age, mail, password):
        super().__init__(name, lastname, age, mail, password)
        self.entrenamientos = []
        self.certificado_entrenador_reconocido = False

    def creacion_plan_entrenamiento(self, titulo, descripcion, tipo_entrenamiento, dificultad, multimedia, metas, otros=False):
        pass
        #if no_of_argu(titulo, descripcion, tipo_entrenamiento, dificultad, multimedia, metas, otros) < 6:
          #  raise WrongNumberOfArguments
            # ver cuando trae un dato erroneo
        #self.entrenamientos.append(PlanEntrenamiento(titulo, descripcion, tipo_entrenamiento, dificultad, multimedia, metas, otros))

    def edicion_plan_entrenamiento(self, entrenamiento):
        pass
        #   editar un entrenamiento y verificar los datos

    def get_listado_entrenamiento(self):
        return self.entrenamientos


class Athlete(User):
    def __init__(self, name, lastname, age, mail, password):
        super().__init__(name, lastname, age, mail, password)
        self.metricas = Metricas()
        self.metas = []
        self.entrenamientos = []

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

    def agregar_entrenamiento_fav(self, entrenamiento):
        self.entrenamientos.append(entrenamiento)

    def eliminar_entrenamiento_fav(self, entrenamiento):
        self.entrenamientos.remove(entrenamiento)

    def entrenamientos_favoritos(self):
        return self.entrenamientos

'''

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