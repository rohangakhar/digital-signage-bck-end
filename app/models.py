# app/models.py
from sqlalchemy import Column, Integer, String
from .database import Base

class Billboard(Base):
    __tablename__ = "billboards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    location = Column(String)
    price = Column(Integer)
