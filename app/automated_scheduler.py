from app import schemas
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.responses import JSONResponse

async def get_schedules_for_next_24_hours(db):
    print("Function to get latest data triggered")
    now = datetime.utcnow()
    next_24_hours = now + timedelta(hours=24)
    print("All billboards' schedules pulled from {now} until {next_24_hours}".format(now=now, next_24_hours=next_24_hours))
    # Get all billboards
    schedules = await db.schedules.find({}).to_list(length=None)
    generated_schedules = []
    for schedule in schedules:
        # Extract schedule info
        billboard_id = schedule['billboard_id']
        schedule_type = schedule['type']
        url = schedule['url']
        start_time = schedule['start_time']
        end_time = schedule['end_time']
        current_time = datetime.utcnow()
        # If the start time has already passed or will start soon
        if start_time <= current_time:
            # Generate hourly records from the current time until the end time or 24 hours
            time_to_check = current_time
            while time_to_check < end_time and time_to_check < current_time + timedelta(hours=24):
                # Generate the schedule record
                new_schedule = {
                    'billboard_id': billboard_id,
                    'type': schedule_type,
                    'url': url,
                    'start_time': time_to_check,
                    'end_time': time_to_check + timedelta(minutes=15)  # Each record lasts for 1 hour
                }
                generated_schedules.append(new_schedule)
                time_to_check += timedelta(minutes=15)
    return generated_schedules

# Function to truncate the schedules_automated collection and reinsert schedules
async def truncate_and_reinsert_schedules(db):
    schedules_to_insert = await get_schedules_for_next_24_hours(db)
    db.schedules_automated.delete_many({})
    if schedules_to_insert:
        db.schedules_automated.insert_many(schedules_to_insert)
        print(f"Reinserted {len(schedules_to_insert)} schedules into schedules_automated.")
    else:
        print("No schedules to insert.")
