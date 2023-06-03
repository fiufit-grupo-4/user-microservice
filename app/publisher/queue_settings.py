from pika.exchange_type import ExchangeType

# ! TODO!!!!  esto es como una " direccion " de la queue a la que deberan conectarse los consumers 
# para escuchar los mensajes que se envian por la queue

EXCHANGE = "get_me_hired_exchange"
EXCHANGE_TYPE = ExchangeType.direct # !TODO investigar q es esto
QUEUE = "get_me_hired_queue"
ROUTING_KEY = "jobs_search"