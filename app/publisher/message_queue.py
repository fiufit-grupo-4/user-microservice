from fastapi import Request, Response

# !TODO hay que definir QUE Enviar por la Queue! De tal forma que del otro lado guarden eso que le enviaremos
# es decir, debemos este protoloco de comunicacion...
# ACA habria que definir QUE REQUESTS en enviar por las queues como metrica!!!
# o sea....... vale la pena enviar todas las requests? capaz el GET /users no vale la pena enviarlo
# fiajrse bien qué metricas pedian para enviar por la queue!
def MesseageQueueFrom(request: Request, response: Response):
    return {
        "url": f'{request.url}',
        "method": f'{request.method}',
        "status_code": f'{response.status_code}',
    }
