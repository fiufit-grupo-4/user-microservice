class Metricas:
    def __init__(self):
        self.distancia_recorrida = 0
        self.tiempo = 0
        self.calorias = 0
        self.hitos = 0
        self.actividad = "No se realizo ninguna metrica"

    def actualizar(self, distancia, tiempo, calorias, hitos, actividad):
        self.distancia_recorrida += distancia
        self.tiempo += tiempo
        self.calorias += calorias
        self.hitos += hitos
        self.actividad = actividad
