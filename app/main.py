from fastapi import FastAPI
from app.controller_example import router as example_router
import pymongo
import logging
from logging.config import dictConfig
from .log_config import logconfig
from os import environ

MONGODB_URI = environ["MONGODB_URI"]

dictConfig(logconfig)
app = FastAPI()
logger = logging.getLogger('app')

logger.error("Error message! - Level 3")
logger.warning("Warning message! - Level 2")
logger.info("Info message! - Level 1")
logger.debug("Debug message! - Level 0")


@app.get("/", tags=["Home"])
def get_root() -> dict:
    return {"message": "OK"}


@app.on_event("startup")
async def startup_db_client():
    try:
        app.mongodb_client = pymongo.MongoClient(MONGODB_URI)
        logger.info("Connected successfully MongoDB")

    except Exception as e:
        logger.error(e)
        logger.error("Could not connect to MongoDB")

    # How to build a collection
    db = app.mongodb_client["example-db"]
    collection = db.example_collection

    collection.delete_many({})  # Clear collection data

    # Add data to collection
    person_1 = {"name": "Agustin", "age": {"$numberInt": "99"}}
    logger.info("Added object with id: %s", collection.insert_one(person_1).inserted_id)
    person_2 = {"name": "Alfonso", "age": {"$numberInt": "10"}}
    logger.info("Added object with id: %s", collection.insert_one(person_2).inserted_id)

    # Check all data in collection
    for p in collection.find():
        logger.warning(p)


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    logger.info("Shutdown APP")


app.include_router(example_router)
