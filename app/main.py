import pymongo
from fastapi import FastAPI
import logging
from logging.config import dictConfig
from .log_config import logconfig
from os import environ
from dotenv import load_dotenv
from app.user.routes_users import router as user_router
from app.auth.login import router as login_router
from app.auth.signup import router as signup_router


load_dotenv()

MONGODB_URI = environ["MONGODB_URI"]

dictConfig(logconfig)
app = FastAPI()
logger = logging.getLogger("app")

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

    # # How to build a collection
    app.database = app.mongodb_client["user_microservice"]
    # users = app.database.users
    # users.delete_many({})  # Clear collection data

    # # Add data to collection
    # person_1 = { "name": "lucas", "lastname": "pepe","age": "20","mail": "pepe@gmail.com"}
    # logger.info("Added object with id: %s", users.insert_one(person_1).inserted_id)
    # person_2 = { "name": "juan", "lastname": "papu","age": "20","mail": "juan@gmail.com"}
    # logger.info("Added object with id: %s", users.insert_one(person_2).inserted_id)

    # # Check all data in collection
    # for p in users.find():
    #     logger.warning(p)


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    logger.info("Shutdown APP")


app.include_router(user_router, tags=["users"], prefix="/users")
app.include_router(login_router, tags=["login"], prefix="/login")
app.include_router(signup_router, tags=["signup"], prefix="/signup")
