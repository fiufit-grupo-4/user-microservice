import os,json
from fastapi import Request, Response
from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
import app.main as main
from app.publisher.message_queue import MesseageQueueFrom
from app.publisher.publisher_queue import getPublisherQueue

publisher = getPublisherQueue()

class PublisherQueueEventMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            publisher.publish_message(MesseageQueueFrom(request, response))
            return response
        except Exception as e:
            main.logger.error(e)
            publisher.publish_message(MesseageQueueFrom(request, Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)))
            raise e
