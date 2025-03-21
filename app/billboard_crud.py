# app/crud.py
from app import schemas
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

def get_collection(db):
    return db.billboards  # You can modify this if your collection name changes

async def create_billboard(db, billboard: schemas.BillboardCreate):
    billboard_dict = billboard.model_dump()
    result = await get_collection(db).insert_one(billboard_dict)
    billboard_dict["id"] = str(result.inserted_id)
    return billboard_dict

async def get_billboard(db, billboard_id: str):
    billboard = await get_collection(db).find_one({"_id": ObjectId(billboard_id)})
    if billboard:
        billboard["id"] = str(billboard["_id"])
    return billboard

async def get_billboards(db, skip: int = 0, limit: int = 100):
    billboards = []
    async for billboard in get_collection(db).find().skip(skip).limit(limit).sort("price", 1):
        billboard["id"] = str(billboard["_id"])
        billboards.append(billboard)
    return billboards

async def update_billboard(db, billboard_id: str, update_data: dict):
    result = await get_collection(db).update_one(
        {"_id": ObjectId(billboard_id)},
        {"$set": update_data},
    )
    if result.matched_count:
        updated_billboard = await get_billboard(db, billboard_id)
        return updated_billboard
    return None

async def delete_billboard(db, billboard_id: str):
    result = await get_collection(db).delete_one({"_id": ObjectId(billboard_id)})
    if result.deleted_count:
        return {"status": "Billboard deleted"}
    return {"status": "Billboard not found"}
