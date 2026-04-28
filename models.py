# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from database import Base

class ImageMetadata(Base):
    __tablename__ = "image_metadata"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    format = Column(String)
    width_px = Column(Integer)
    height_px = Column(Integer)
    color_mode = Column(String)
    file_size_kb = Column(Float)

    # JSONB column to store the flexible EXIF dictionary
    exif_data = Column(JSONB, nullable=True) 

    upload_timestamp = Column(DateTime, default=datetime.utcnow)