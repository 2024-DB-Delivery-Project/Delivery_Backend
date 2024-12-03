from fastapi import FastAPI
from app.app import app
from app.routers import users, customers

app.include_router(users.router)
app.include_router(customers.router)

@app.get("/")
def root():
    return {"message": "Hello World"}