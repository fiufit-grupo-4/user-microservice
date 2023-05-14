from fastapi import HTTPException
import requests
import app.main as main
from starlette import status
from app.settings.config import TRAINING_SERVICE_URL


class ServiceTrainers:
    @staticmethod
    def get(path):
        try:
            result = requests.get(TRAINING_SERVICE_URL + f'{path}')
            return result
        except Exception:
            main.logger.error('Training service cannot be accessed')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Training service cannot be accessed',
            )
