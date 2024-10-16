from pydantic import BaseModel
from datetime import datetime

class MedicalDataTransformationCreate(BaseModel):
    pass

class MedicalDataTransformationBase(BaseModel):
    channel_title: str
    channel_username: str
    message:str
    date:datetime
    media_path: str

    class Config:
        from_attributes = True

