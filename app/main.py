import pymongo
from fastapi import FastAPI, Request
import logging
from logging.config import dictConfig

import uvicorn
from .log_config import logconfig
from os import environ
from dotenv import load_dotenv
from .urls import api_router

load_dotenv()

MONGODB_URI = environ["MONGODB_URI"]

dictConfig(logconfig)
app = FastAPI()
logger = logging.getLogger("app")


@app.get("/", tags=["Home"])
def get_root(request: Request) -> dict:
    app.logger.warning(f"GET {request.url} | PATH {request.url.path} | FROM {request.client} | HEADERS {request.headers} | COOKIES {request.cookies}")
    return {"message": "OK"}


@app.on_event("startup")
async def startup_db_client():
    try:
        app.mongodb_client = pymongo.MongoClient(MONGODB_URI)
        logger.info("Connected successfully MongoDB")

    except Exception as e:
        logger.error(e)
        logger.error("Could not connect to MongoDB")

    app.logger = logger
    app.database = app.mongodb_client["user_microservice"]
    # app.database.users.delete_many({})


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    logger.info("Shutdown APP")


app.include_router(api_router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
