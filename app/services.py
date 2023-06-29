from fastapi import HTTPException
import httpx
from app.config.config import Settings
import app.main as main
from starlette import status

app_settings = Settings()


class ServiceTrainers:
    @staticmethod
    async def get(path):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(app_settings.TRAINING_SERVICE_URL + path)
                return response
        except Exception:
            main.logger.error('Training service cannot be accessed')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Training service cannot be accessed',
            )
