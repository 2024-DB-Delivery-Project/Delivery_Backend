from fastapi import FastAPI
from app.app import app
from app.routers import users

app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Hello World"}