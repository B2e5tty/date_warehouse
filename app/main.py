import sys
import os

sys.path.append("/app")

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post('/medical_data_transformations/', response_model=schemas.MedicalDataTransformationBase)
def create_medical_data_transformation(item:schemas.MedicalDataTransformationCreate, db: Session = Depends(get_db)):
    return crud.create_medical_data_transformation(db=db, transformation=item)

@app.get("/medical_data_transformations/",response_model=list[schemas.MedicalDataTransformationBase])
def read_medical_data_transformations(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = crud.get_medical_data_transformations(db, skip=skip, limit=limit)
    return items
@app.get("/medical_data_transformations/{item_id}", response_model=schemas.MedicalDataTransformationBase)
def read_medical_data_transformation(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_medical_data_transformation(db,item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item
