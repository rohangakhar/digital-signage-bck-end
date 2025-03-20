# app/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
import os

client = None
db = None

async def init_db(app: FastAPI):
    global client, db
    client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client.get_database("digital_signage")  # Use your desired DB name
    app.state.db = db

def get_db():
    return db
