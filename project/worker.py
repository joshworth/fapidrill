import os
import time
from datetime import datetime
from celery import Celery
from sqlalchemy import desc
from repo import db_crud, ItemCreate
from repo import SessionLocal, db_session
import logging


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get(
    "CELERY_BROKER_URL",
    "redis://localhost:6379"
)
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND",
    "redis://localhost:6379"
)


class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db_session.remove()


@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    try:
        logging.info("SESSION CREATE ---- ")
        # call databse, create an item based on type and time
        db = SessionLocal()
        items = db_crud.get_items(db=db)
        x_time = datetime.now().time().strftime("%H-%M-%S")
        tcount = len(items)
        item_name = f"Item no - {tcount-1}"
        item_desc = f"log type {task_type} at {x_time} - {tcount} - items"
        item_create = ItemCreate(
            title=item_name,
            description=item_desc
        )
        db_crud.create_user_item(
            db=db,
            item=item_create,
            user_id=2
        )
    except Exception as xx:
        logging.error("Error: ", xx)
        print("ERROR:", xx)
    finally:
        db.close()

    return True
