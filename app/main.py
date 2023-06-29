import asyncio
import pymongo
import logging
import uvicorn
import firebase_admin

from fastapi import FastAPI
from logging.config import dictConfig
from app.config.log_config import logconfig
from app.config.config import Settings
from app.publisher.publisher_queue import runPublisherManager
from app.publisher.publisher_queue_middleware import PublisherQueueEventMiddleware
from .urls import api_router
from firebase_admin import credentials
from app.config.credentials import firebase_credentials


dictConfig(logconfig)
app = FastAPI()
app_settings = Settings()
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
logger = logging.getLogger("app")

app.add_middleware(PublisherQueueEventMiddleware)


@app.on_event("startup")
async def startup_db_client():
    try:
        app.mongodb_client = pymongo.MongoClient(app_settings.MONGODB_URI)
        logger.info("Connected successfully MongoDB")
    except Exception as e:
        logger.error(e)
        logger.error("Could not connect to MongoDB")

    app.logger = logger
    app.database = app.mongodb_client["user_microservice"]
    app.task_publisher_manager = asyncio.create_task(runPublisherManager())

    # app.database.users.delete_many({})


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    app.task_publisher_manager.cancel()
    logger.info("Shutdown APP")


app.include_router(api_router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=app_settings.PORT)
