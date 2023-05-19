from fastapi import HTTPException
import httpx
import app.main as main
from starlette import status
from app.settings.config import TRAINING_SERVICE_URL


class ServiceTrainers:
    @staticmethod
    async def get(path):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(TRAINING_SERVICE_URL + path)
                return response
        except Exception:
            main.logger.error('Training service cannot be accessed')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Training service cannot be accessed',
            )
