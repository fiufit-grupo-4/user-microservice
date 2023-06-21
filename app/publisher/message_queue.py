from fastapi import Request, Response
import datetime
import logging
from geopy.geocoders import Nominatim

from app.definitions import (
    ADD_TRAINING_TO_FAVS,
    BLOCK,
    GOOGLE_SIGNUP,
    REMOVE_TRAINING_FROM_FAVS,
    USER_EDIT,
    SIGNUP,
    UNBLOCK,
)


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
    training_id = ""
    user_id = ""

    try:
        user_id = request.state.user_id
        action = request.state.action
        geolocator = Nominatim(user_agent="app")

        if action in (SIGNUP, GOOGLE_SIGNUP):
            coordinates = request.state.location.__dict__
            location = geolocator.reverse(
                [coordinates['latitude'], coordinates['longitude']]
            )
            country = location.raw['address']['country']
        elif action in (ADD_TRAINING_TO_FAVS, REMOVE_TRAINING_FROM_FAVS):
            training_id = request.state.training_id
            coordinates = request.state.location
            location = geolocator.reverse(
                [coordinates['latitude'], coordinates['longitude']]
            )
            country = location.raw['address']['country']
        elif request.state.location_edit:
            coordinates = request.state.location
            location = geolocator.reverse(
                [coordinates['latitude'], coordinates['longitude']]
            )
            country = location.raw['address']['country']

    except Exception as e:
        logger.info(e)
        pass

    return {
        "service": "user-service",
        "path": f'{request.url.path}',
        "url": f'{request.url}',
        "method": f'{request.method}',
        "status_code": f'{response.status_code}',
        "datetime": f'{formatted_datetime}',
        "response_time": f'{response_time}',
        "user_id": f'{user_id}',
        "ip": f'{request.client.host}',
        "country": f'{country}',
        "action": f'{action}',
        "training_id": f'{training_id}',
        "training_type": "",
    }
