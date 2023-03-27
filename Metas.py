class Meta:
    def __init__(self, titulo, descripcion, metrica, limite_tiempo):
        self.titulo = titulo
        self.descripcion = descripcion
        self.metrica = metrica
        self.limite_tiempo = limite_tiempo
        self.cumplida = False

    def actualizar(self, titulo, descripcion, metrica, limite_tiempo):
        self.titulo = titulo
        self.descripcion = descripcion
        self.metrica = metrica
        self.limite_tiempo = limite_tiempo

    def visualizar(self):
        pass
        # todavia no se que se debe visualizar ni como devolverlo

    def cumplida(self):
        self.cumplida = True