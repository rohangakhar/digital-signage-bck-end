from app import schemas
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.responses import JSONResponse


# Utility function to get the schedules collection
def get_collection(db):
    return db.schedules  # MongoDB collection name for schedules

def get_billboards_collection(db):
    return db.billboards

# Create a new schedule
async def create_schedule(db, schedule: schemas.ScheduleCreate):
    current_time = datetime.utcnow()
    end_time_naive = schedule.end_time.replace(tzinfo=None)
    try:
        billboard = await get_billboards_collection(db).find_one({"_id": ObjectId(schedule.billboard_id)})
    except:
        raise HTTPException(status_code=400,detail = "InvalidId: {ID} is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string".format(ID = schedule.billboard_id))
    if not billboard:
        raise HTTPException(status_code=400, detail="Billboard with ID {schedule.billboard_id} does not exist.")
    if(end_time_naive<current_time):
        raise HTTPException(status_code=400, detail="Please book the slot for future time")
    if(schedule.start_time > schedule.end_time):
        raise HTTPException(status_code=400, detail="Start time can't be ahead of End time")
    schedule_dict = schedule.model_dump()
    existing_schedule = await get_collection(db).find_one({
        "billboard_id": schedule.billboard_id,
        "$or": [
            {
            "start_time": {"$lt": schedule.end_time}, "end_time": {"$gt": schedule.start_time}   # New schedule ends after existing schedule starts
            }
        ]
    })
    
    if existing_schedule:
        current_end_time = existing_schedule["end_time"]
        new_end_time = end_time_naive
        if new_end_time > current_end_time:
            result = await db.schedules.update_one(
                {"billboard_id": schedule.billboard_id},
                {"$set": {"end_time": new_end_time}}
            )
    final_result =  await get_collection(db).find_one({"billboard_id": schedule.billboard_id})
    final_result['id'] = str(final_result['_id'])
    del final_result['_id']
    return final_result

# Get a schedule by Billboard_ID
async def get_schedule(db, billboard_id: str):
    schedule_list = db.schedules.find({ "billboard_id": billboard_id })
    schedule_list = await schedule_list.to_list(length=None)   
    for schedule in schedule_list:
        schedule['id'] = str(schedule['_id'])  # Convert ObjectId to string
        del schedule['_id']
    #make sure to send only schedules which are for next 24 hours    

    return schedule_list

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