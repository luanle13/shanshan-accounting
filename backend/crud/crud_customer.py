from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.customer import Customer
from ..schemas.customer import CustomerCreate, CustomerUpdate

def get_customer(db: Session, customer_id: int):
    return db.query(Customer).filter(Customer.id == customer_id).first()


def get_customers(db: Session, skip: int = 0, limit: int = 100):
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
        
        db_customer.updated_on = db_customer.__class__.updated_on.default.arg  # Update timestamp
        
        db.commit()
        db.refresh(db_customer)
    
    return db_customer


def delete_customer(db: Session, customer_id: int):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if db_customer:
        db.delete(db_customer)
        db.commit()
    
    return db_customer