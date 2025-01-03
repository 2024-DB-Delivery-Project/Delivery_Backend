from fastapi import FastAPI
from app.app import app
from app.routers import users, customers, seller, logistic, driver

app.include_router(users.router)
app.include_router(customers.router)
app.include_router(seller.router)
app.include_router(logistic.router)
app.include_router(driver.router)

@app.get("/")
def root():
    return {"message": "Hello World"}