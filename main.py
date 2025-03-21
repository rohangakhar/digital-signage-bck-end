# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from app import billboard_crud, schemas, database, schedule_crud, automated_scheduler
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import asyncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8010",
    "http://127.0.0.1:8010",
    "http://localhost:8081",
    "http://127.0.0.1:8081"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins specified above
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup_db():
    await database.init_db(app)
    start_scheduler()

@app.post("/billboards/", response_model=schemas.Billboard)
async def create_billboard(billboard: schemas.BillboardCreate, db=Depends(database.get_db)):
    created_billboard = await billboard_crud.create_billboard(db, billboard)
    return created_billboard

@app.get("/billboards/{billboard_id}", response_model=schemas.Billboard)
async def read_billboard(billboard_id: str, db=Depends(database.get_db)):
    db_billboard = await billboard_crud.get_billboard(db, billboard_id)
    if db_billboard is None:
        raise HTTPException(status_code=404, detail="Billboard not found")
    return db_billboard

@app.get("/billboards/", response_model=list[schemas.Billboard])
async def read_billboards(skip: int = 0, limit: int = 100, db=Depends(database.get_db)):
    return await billboard_crud.get_billboards(db, skip, limit)

@app.put("/billboards/{billboard_id}", response_model=schemas.Billboard)
async def update_billboard(billboard_id: str, billboard: schemas.BillboardCreate, db=Depends(database.get_db)):
    updated_billboard = await billboard_crud.update_billboard(db, billboard_id, billboard.dict())
    if updated_billboard is None:
        raise HTTPException(status_code=404, detail="Billboard not found")
    return updated_billboard

@app.delete("/billboards/{billboard_id}", response_model=schemas.Billboard)
async def delete_billboard(billboard_id: str, db=Depends(database.get_db)):
    result = await billboard_crud.delete_billboard(db, billboard_id)
    if "status" in result and result["status"] == "Billboard deleted":
        return JSONResponse(status_code=200, content=result)
    raise HTTPException(status_code=404, detail="Billboard not found")

# Endpoint to create a schedule
@app.post("/schedules/", response_model=schemas.Schedule)
async def create_schedule(schedule: schemas.ScheduleCreate, db=Depends(database.get_db)):
    created_schedule = await schedule_crud.create_schedule(db, schedule)
    return created_schedule

# Endpoint to get a schedule by Billboard ID
@app.get("/schedules/{billboard_id}", response_model=list[schemas.Schedule])
async def read_schedule(billboard_id: str, db=Depends(database.get_db)):
    db_schedule = await schedule_crud.get_schedule(db, billboard_id)
    return db_schedule if db_schedule else []

# Endpoint to get all schedules with pagination
@app.get("/schedules/", response_model=list[schemas.Schedule])
async def read_schedules(skip: int = 0, limit: int = 100, db=Depends(database.get_db)):
    return await schedule_crud.get_schedules(db, skip, limit)

# Endpoint to update a schedule by ID
@app.put("/schedules/{schedule_id}", response_model=schemas.Schedule)
async def update_schedule(schedule_id: str, schedule: schemas.ScheduleCreate, db=Depends(database.get_db)):
    updated_schedule = await schedule_crud.update_schedule(db, schedule_id, schedule.dict())
    return updated_schedule if updated_schedule else []

# Endpoint to delete a schedule by ID
@app.delete("/schedules/{schedule_id}", response_model=schemas.Schedule)
async def delete_schedule(schedule_id: str, db=Depends(database.get_db)):
    result = await schedule_crud.delete_schedule(db, schedule_id)
    if "status" in result and result["status"] == "Schedule deleted":
        return JSONResponse(status_code=200, content=result)
    raise HTTPException(status_code=404, detail="Schedule not found")

@app.post("/login")
async def login(user: schemas.User):
    if user.username =='admin' and user.password == 'admin':
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
@app.get("/schedules_synced/{billboard_id}", response_model=list[schemas.Schedule])
async def schedules_synced(billboard_id:str, db=Depends(database.get_db)):
    db_schedule = await schedule_crud.schedules_synced(db, billboard_id)
    return db_schedule if db_schedule else []
@app.post("/test")
async def test(db=Depends(database.get_db)):
    await automated_scheduler.truncate_and_reinsert_schedules(db)

async def automated_reschedules(db):
    await automated_scheduler.truncate_and_reinsert_schedules(db)


# APScheduler background job function
def start_scheduler():
    scheduler = BackgroundScheduler()
    loop = asyncio.get_event_loop()

    # Create a job that triggers every 15 minutes
    scheduler.add_job(
        lambda: asyncio.run_coroutine_threadsafe(automated_reschedules(database.get_db()), loop),
        IntervalTrigger(minutes=15),
        id='truncate_and_reinsert_job',  # Unique job ID
        name='Truncate and reinsert schedules every 15 minutes',
        replace_existing=True  # Replaces the job if it already exists
    )

    # Start the scheduler
    scheduler.start()
    