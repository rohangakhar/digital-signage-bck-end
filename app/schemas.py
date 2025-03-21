# app/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import Literal

class BillboardBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: str
    price: int

class BillboardCreate(BillboardBase):
    pass

class Billboard(BillboardBase):
    id: str  # MongoDB uses _id as the identifier, so we will map it to 'id'

    class Config:
        orm_mode = True

class ScheduleBase(BaseModel):
    billboard_id: str  # The billboard being shown
    type: Literal['Video', 'Image']  # Now optional
    url: Optional[str] 
    start_time: datetime  # When the schedule starts
    end_time: datetime  # When the schedule ends
    
    class Config:
        # Allow datetime parsing with timezone
        # This will allow `datetime` fields to be parsed correctly with timezone
        json_encoders = {
            datetime: lambda v: v.isoformat()  # For converting datetime to ISO string (with timezone)
        }

class ScheduleCreate(ScheduleBase):
    pass

class User(BaseModel):
    username: str
    password: str

class Schedule(ScheduleBase):
    id: str  # MongoDB document ID (string)

    class Config:
        orm_mode = True
