from pika.exchange_type import ExchangeType

# Esto es como una "direccion" de la queue a la que debera conectarse los productores
# para enviar los mensajes, y los consumidores para escuchar los mensajes que se envian 

EXCHANGE = "fiutfit-metrics-exchange"
EXCHANGE_TYPE = ExchangeType.direct
QUEUE = "fiufit-metrics-queue"
ROUTING_KEY = "fiufit-metrics"