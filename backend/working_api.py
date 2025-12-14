from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import os

# Database setup
DATABASE_URL = "sqlite:///./shanshan_accounting.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Base class with common fields
class TimestampMixin:
    """Mixin class to add timestamps and user tracking to models"""
    created_on = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))

# Customer model
class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)

# Pydantic schemas
class CustomerBase(BaseModel):
    name: str
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    name: Optional[str] = None

class Customer(CustomerBase):
    id: int
    created_on: datetime
    updated_on: datetime

    class Config:
        from_attributes = True

# CRUD operations
def get_customer(db: Session, customer_id: int):
    return db.query(Customer).filter(Customer.id == customer_id).first()

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    from sqlalchemy import desc
    return db.query(Customer).order_by(desc(Customer.created_on)).offset(skip).limit(limit).all()

def create_customer(db: Session, customer: CustomerCreate, created_by: str = None):
    db_customer = Customer(
        name=customer.name,
        created_by=created_by,
        updated_by=created_by
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def update_customer(db: Session, customer_id: int, customer: CustomerUpdate, updated_by: str = None):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if db_customer:
        # Update the fields that were provided
        if customer.name is not None:
            db_customer.name = customer.name
        if updated_by:
            db_customer.updated_by = updated_by
        
        db_customer.updated_on = datetime.utcnow()
        
        db.commit()
        db.refresh(db_customer)
    
    return db_customer

def delete_customer(db: Session, customer_id: int):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if db_customer:
        db.delete(db_customer)
        db.commit()
    
    return db_customer

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI app
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

# Endpoints for customers
@app.post("/customers/", response_model=Customer)
def create_customer_endpoint(customer: CustomerCreate, db: Session = Depends(get_db)):
    return create_customer(db=db, customer=customer)

@app.get("/customers/{customer_id}", response_model=Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@app.get("/customers/", response_model=List[Customer])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = get_customers(db, skip=skip, limit=limit)
    return customers

@app.put("/customers/{customer_id}", response_model=Customer)
def update_customer_endpoint(
    customer_id: int, 
    customer: CustomerUpdate, 
    db: Session = Depends(get_db)
):
    db_customer = update_customer(db, customer_id=customer_id, customer=customer)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@app.delete("/customers/{customer_id}", response_model=Customer)
def delete_customer_endpoint(customer_id: int, db: Session = Depends(get_db)):
    db_customer = delete_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@app.get("/")
def read_root():
    return {"message": "Welcome to Shanshan Accounting API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)