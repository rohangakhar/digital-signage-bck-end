# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from app import billboard_crud, schemas, database, schedule_crud
from fastapi.responses import JSONResponse

app = FastAPI()

@app.on_event("startup")
async def startup_db():
    await database.init_db(app)

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
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return db_schedule

# Endpoint to get all schedules with pagination
@app.get("/schedules/", response_model=list[schemas.Schedule])
async def read_schedules(skip: int = 0, limit: int = 100, db=Depends(database.get_db)):
    return await schedule_crud.get_schedules(db, skip, limit)

# Endpoint to update a schedule by ID
@app.put("/schedules/{schedule_id}", response_model=schemas.Schedule)
async def update_schedule(schedule_id: str, schedule: schemas.ScheduleCreate, db=Depends(database.get_db)):
    updated_schedule = await schedule_crud.update_schedule(db, schedule_id, schedule.dict())
    if updated_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return updated_schedule

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
    
# @app.get("/dayschedules")
# async def read_schedules_24_hours(db=Depends(database.get_db), skip: int = 0, limit: int = 100):
#     return await schedule_crud.get_schedules_24(db, skip, limit)