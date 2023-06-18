from fastapi import Request, Response
import datetime
import logging
import json
from geopy.geocoders import Nominatim

from app.definitions import BLOCK, GOOGLE_SIGNUP, USER_EDIT, SIGNUP, UNBLOCK


logger = logging.getLogger('app')


def MessageQueueFrom(
    request: Request, response: Response, timestamp: float, response_time: float
):

    date_time = datetime.datetime.fromtimestamp(timestamp)
    formatted_datetime = date_time.strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )  # datetime obj to ISO 8601 format

    action = ""
    country = ""

    try:
        action = request.state.action
        geolocator = Nominatim(user_agent="app")
        if action in (SIGNUP, GOOGLE_SIGNUP):
            coordinates = request.state.location.__dict__
            location = geolocator.reverse(
                [coordinates['latitude'], coordinates['longitude']]
            )
            country = location.raw['address']['country']
            logger.critical(country)
        elif request.state.location_edit:
            logger.critical(country)
            coordinates = request.state.location
            location = geolocator.reverse(
                [coordinates['latitude'], coordinates['longitude']]
            )
            country = location.raw['address']['country']

    except Exception as e:
        logger.critical(e)
        pass

    return {
        "service": "user-service",
        "path": f'{request.url.path}',
        "url": f'{request.url}',
        "method": f'{request.method}',
        "status_code": f'{response.status_code}',
        "datetime": f'{formatted_datetime}',
        "response_time": f'{response_time}',
        "user_id": f'{request.state.user_id}',
        "ip": f'{request.client.host}',
        "country": f'{country}',
        "action": f'{action}',
        "training_id": "",
        "training_type": "",
    }
