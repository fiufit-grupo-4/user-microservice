from fastapi import FastAPI
from app.controller_example import router as example_router
import pymongo
import logging
from logging.config import dictConfig
from fastapi import FastAPI
from .log_config import logconfig

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
        app.mongodb_client = pymongo.MongoClient("mongodb:27017")
        logger.info("Connected successfully MongoDB")
    except Exception as e:  # !!!
        logger.error(e)
        logger.error("Could not connect to MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    logger.info("Shutdown APP")

app.include_router(example_router)
