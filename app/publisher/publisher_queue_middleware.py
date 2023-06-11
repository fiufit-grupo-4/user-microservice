import os,json
from fastapi import Request, Response
from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
import app.main as main
from app.publisher.message_queue import MessageQueueFrom
from app.publisher.publisher_queue import getPublisherQueue
import datetime

publisher = getPublisherQueue()

class PublisherQueueEventMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_timestamp = datetime.datetime.now().timestamp()
        try:
            response = await call_next(request)
            end_timestamp = datetime.datetime.now().timestamp()
            if request.state.metrics_allowed:
                publisher.publish_message(MessageQueueFrom(request, response, start_timestamp, end_timestamp - start_timestamp))
            return response
        except AttributeError as e: # 'State' object has no attribute 'metrics_allowed'
            main.logger.info(e)
            return response
        except Exception as e:
            main.logger.error(e)
            publisher.publish_message(MessageQueueFrom(request, Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR), start_timestamp, 0))
            raise e
