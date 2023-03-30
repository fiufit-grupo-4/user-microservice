from fastapi import FastAPI
from app.controller_example import router as example_router
import pymongo

app = FastAPI()


@app.get("/", tags=["Home"])
def get_root() -> dict:
    return {"message": "OK"}


@app.on_event("startup")
async def startup_db_client():
    try:
        app.mongodb_client = pymongo.MongoClient("mongodb:27017")
        print("Connected successfully!")
    except Exception as e:  # !!!
        print(e)
        print("Could not connect to MongoDB")


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(example_router)
