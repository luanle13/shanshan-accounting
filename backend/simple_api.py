from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager
import sys
import os

# Add the current directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from database.database import engine, Base
from routes import customers

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Any cleanup code can go here if needed

app = FastAPI(
    title="Shanshan Accounting API",
    description="Backend API for Shanshan Accounting system",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(customers.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Shanshan Accounting API"}

# For testing, add a simple endpoint
@app.get("/test")
def test():
    return {"message": "Test successful"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)