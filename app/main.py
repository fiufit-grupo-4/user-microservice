from fastapi import FastAPI

app = FastAPI()

@app.get("/", tags=["Home"])
def get_root() -> dict:
    return {
        "message": "Hello Pach!"
    }