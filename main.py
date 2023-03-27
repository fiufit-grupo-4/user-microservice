from fastapi import FastAPI
from user import *

app = FastAPI()


@app.get("/")
def read_root():
    return User("Tizziana", "Mazza", 25, "tizzianamazza@gmail.com", "lala1")

@app.get("/tizziana")
def titi():
    return {"Tizzi": "saluda"}