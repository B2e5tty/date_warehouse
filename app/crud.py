from sqlalchemy.orm import Session
import models, schemas

def get_medical_data_transformation(db: Session, item_id: int):
    return db.query(models.MedicalTransformation).filter(models.MedicalTransformation.id == item_id).first()

def get_medical_data_transformations(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.MedicalTransformation).offset(skip).limit(limit).all()

def create_medical_data_transformation(db: Session, transformation: schemas.MedicalDataTransformationCreate):
    db_transformation = models.MedicalTransformation(**transformation.dict())
    db.add(db_transformation)
    db.commit()
    db.refresh(db_transformation)
    return db_transformation 