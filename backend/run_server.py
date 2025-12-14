import sys
import os
from contextlib import asynccontextmanager

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import customers
from database.database import engine, Base
import uvicorn

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(customers.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Shanshan Accounting API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)