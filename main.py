from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine, Base
from models import Item

app=FastAPI()

Base.metadata.create_all(bind=engine)

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request and response
class ItemCreate(BaseModel):
    name: str
    description: str
    price: float
    quantity: int

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None

class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int

    class Config:
        orm_mode = True


@app.post("/items/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """
    Create a new item in the database.
    :param item: ItemCreate object containing name, description, price, and quantity
    :param db: Database session
    :return: The created item
    """
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=List[ItemResponse])
def get_items(db: Session = Depends(get_db)):
    """
    Retrieve all items from the database.
    :param db: Database session
    :return: List of items
    """
    return db.query(Item).all()


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """
    Retrieve an item by its ID.
    :param item_id: ID of the item to retrieve
    :param db: Database session
    :return: The item with the specified ID
    """
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    """
    Update an item by its ID.
    :param item_id: ID of the item to update
    :param item: ItemUpdate object containing updated fields
    :param db: Database session
    :return: The updated item
    """
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for var, value in vars(item).items():
        if value is not None:
            setattr(db_item, var, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """
    Delete an item by its ID.
    :param item_id: ID of the item to delete
    :param db: Database session
    :return: Confirmation message
    """
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"detail": "Item deleted"}

