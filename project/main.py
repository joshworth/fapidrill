from fastapi import Body, FastAPI, Request, Depends,HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from worker import create_task
from celery.result import AsyncResult
from sqlalchemy.orm import Session
from repo import SessionLocal, engine
from repo import db_crud
from typing import List
from repo import Base
from repo import UserIndb, UserCreate, ItemIndb, ItemCreate
import logging
from datetime import datetime

logging.basicConfig(filename='main.log', encoding='utf-8', level=logging.INFO)
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "home.html", context={"request": request}
    )


@app.post("/tasks", status_code=201)
def run_task(
    payload=Body(...),
    db: Session = Depends(get_db)
):

    x_time = datetime.now().time().strftime("%H-%M-%S")
    item_name = f"Item at {x_time} - 1xxxxxxxx"
    item_create = ItemCreate(
            title=item_name,
            description="1"
        )
    db_crud.create_user_item(
        db=db,
        item=item_create,
        user_id=1
    )
    task_type = payload["type"]
    task = create_task.delay(int(task_type))

    item_name = f"Item at {x_time} - 2xxxxxx"
    item_create = ItemCreate(
            title=item_name,
            description="2"
        )
    db_crud.create_user_item(
        db=db,
        item=item_create,
        user_id=1
    )
    return JSONResponse({"task_id": task.id})


@app.get("/tasks/{task_id}")
def get_status(task_id, db: Session = Depends(get_db)):
    task_result = AsyncResult(task_id)
    items = db_crud.get_items(db=db)
    total_count = len(items)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
        "total_count": total_count
    }
    return JSONResponse(result)


@app.post("/tasks-2", status_code=201)
def run_task_2(payload=Body(...)):
    task_type = payload["type"]
    task = create_task.delay(int(task_type))
    return JSONResponse({"task_id": task.id})


@app.get("/tasks-2/{task_id}")
def get_status_2(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)


@app.post("/users/", response_model=UserIndb)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    db_user = db_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return db_crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[UserIndb])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db_crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=UserIndb)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=ItemIndb)
def create_item_for_user(
    user_id: int, item: ItemCreate, db: Session = Depends(get_db)
):
    return db_crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=List[ItemIndb])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db_crud.get_items(db, skip=skip, limit=limit)
    return items
