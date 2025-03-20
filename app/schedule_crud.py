from app import schemas
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from datetime import datetime, timedelta

# Utility function to get the schedules collection
def get_collection(db):
    return db.schedules  # MongoDB collection name for schedules

# Create a new schedule
async def create_schedule(db, schedule: schemas.ScheduleCreate):
    schedule_dict = schedule.model_dump()
    result = await get_collection(db).insert_one(schedule_dict)
    schedule_dict["id"] = str(result.inserted_id)
    return schedule_dict

# Get a schedule by ID
async def get_schedule(db, schedule_id: str):
    schedule = await get_collection(db).find_one({"_id": ObjectId(schedule_id)})
    if schedule:
        schedule["id"] = str(schedule["_id"])
    return schedule

# Get all schedules with pagination
async def get_schedules(db, skip: int = 0, limit: int = 100):
    schedules = []
    async for schedule in get_collection(db).find().skip(skip).limit(limit):
        schedule["id"] = str(schedule["_id"])
        schedules.append(schedule)
    return schedules

# Update a schedule by ID
async def update_schedule(db, schedule_id: str, update_data: dict):
    result = await get_collection(db).update_one(
        {"_id": ObjectId(schedule_id)},
        {"$set": update_data},
    )
    if result.matched_count:
        updated_schedule = await get_schedule(db, schedule_id)
        return updated_schedule
    return None

# Delete a schedule by ID
async def delete_schedule(db, schedule_id: str):
    result = await get_collection(db).delete_one({"_id": ObjectId(schedule_id)})
    if result.deleted_count:
        return {"status": "Schedule deleted"}
    return {"status": "Schedule not found"}

async def get_schedules_24(db, skip: int = 0, limit: int = 100):
    # Get the current time
    current_time = datetime.utcnow()

    # Calculate the time range (current_time - 1 hour) and (current_time + 24 hours)
    start_times = current_time - timedelta(hours=1)
    end_times = current_time + timedelta(hours=24)

    # Filter the collection based on the time range
    query = {
        "start_time": {
            "$gt": start_times,  # greater than current_time - 1 hour
            "$lte": end_times    # less than or equal to current_time + 24 hours
        }
    }

    # Fetch the filtered schedules from the database
    schedules = []
    async for schedule in get_collection(db).find(query).skip(skip).limit(limit):
        # Convert the ObjectId to a string and add to the schedule
        schedule["id"] = str(schedule["_id"])  # This is where we convert the ObjectId to a string
        del schedule["_id"]  # Optional: remove the _id field if you prefer to only return 'id'

        # Add schedule to the list
        schedules.append(schedule)

    return schedules