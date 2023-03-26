from user import *
#ver la posibilidad de que el usuario reciba un perfil con todos sus datos
perfil = Profile("Juan Perez", 20)
# usuario = User("Juan Perez", 20)
usuario = User(perfil)

print(usuario.getAge())
print(usuario.getName())