class Meta:
    def __init__(self, titulo, descripcion, metrica, limite_tiempo):
        self.titulo = titulo
        self.descripcion = descripcion
        self.metrica = metrica
        self.limite_tiempo = limite_tiempo

    def actualizar(self, titulo, descripcion, metrica, limite_tiempo):
        self.titulo = titulo
        self.descripcion = descripcion
        self.metrica = metrica
        self.limite_tiempo = limite_tiempo

