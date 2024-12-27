from pydantic import BaseModel
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from celery.result import AsyncResult
import time
from celery import Celery
import redis.asyncio as redis
app = FastAPI()
url = "redis://redis:6379/0"
# Initialize Celery
celery_app = Celery('worker', broker='redis://redis:6379/0', backend='redis://redis:6379/0')


class Input(BaseModel):
    n: int

import json


async def get_master_connexion_aio(url: str) -> redis.Redis:
    
    conn = redis.from_url(url, decode_responses=True)
    return conn



@app.post("/start-task/")
async def start_task(input: Input):
    n=input.n
    task = celery_app.send_task('worker.fibonacci', args=[n])
    conn = await get_master_connexion_aio(url)
    pubsub = conn.pubsub()
    await pubsub.subscribe('task_updates')

    async def event_stream():
        task_completed = False
        while not task_completed:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            
            if message:
                task_id, update = message['data'].split(':')
                print(update)    
                if task_id == task.id:
                    yield f"data: {update}\n\n"
                    if "Completed" in update:
                        task_completed = True
    

    return StreamingResponse(event_stream(), media_type="text/event-stream")

