from fastapi import Request, Response
import datetime
import logging


def MessageQueueFrom(request: Request, response: Response, timestamp: float, response_time: float):

    date_time = datetime.datetime.fromtimestamp(timestamp)
    formatted_datetime = date_time.strftime("%Y-%m-%d %H:%M:%S.%f") # datetime obj to ISO 8601 format

    ip = request.client.host
    country = None
    city = None


    logging.warning(f"REQUEST: {request}")

    return {
        "service" : "user-service",
        "path": f'{request.url.path}',
        "url": f'{request.url}',
        "method": f'{request.method}',
        "status_code": f'{response.status_code}',
        "datetime": f'{formatted_datetime}',
        "response_time": f'{response_time}',
        "ip": f'{ip}',
        "country": f'{country}',
        "city": f'{city}'
    }
