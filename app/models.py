from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class MedicalTransformation(Base):
    __tablename__ = "medical_data_transformation"

    channel_title = Column("Channel Title", String)
    channel_username = Column("Channel Username", String)
    id = Column("ID", Integer, primary_key=True)
    message = Column("Message", String)
    date = Column("Date", DateTime)
    media_path = Column("Media Path", String)
