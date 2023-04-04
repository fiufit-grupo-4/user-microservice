import uuid
from typing import Optional, Collection

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr


def validate_username(username, users):
    for user in users.find():
        if user.name == username:
            return False
    return True


def create_user(name: str, lastname: str, mail: str, age: str, data_base : Collection):
    user_id = str(uuid.uuid4())
    new_user = User(user_id=user_id, name=name, lastname=lastname, mail=mail, age=age)
    new_user = jsonable_encoder(new_user)
    data_base.insert_one(new_user)
    return new_user

class UserRequest(BaseModel):
    name: str
    lastname: str
    mail: Optional[EmailStr]
    age: str


class UserResponse(BaseModel):
    user_id: str
    name: str
    lastname: str
    age: str
    mail: Optional[EmailStr]

    class Config:
        orm_mode = True


class UpdateUserRequest(BaseModel):
    mail: EmailStr

class User:
    def __init__(self, user_id, name, lastname, age, mail):  # password=""):
        self.user_id = user_id
        self.name = name
        self.lastname = lastname
        self.age = age
        self.mail = mail

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
