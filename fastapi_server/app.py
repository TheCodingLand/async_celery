from pydantic import BaseModel
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from celery.result import AsyncResult
import time
from celery import Celery
import aioredis
app = FastAPI()

# Initialize Celery
celery_app = Celery('worker', broker='redis://redis:6379/0', backend='redis://redis:6379/0')


class Input(BaseModel):
    n: int

import json


@app.post("/start-task/")
async def start_task(input: Input):
    n=input.n
    task = celery_app.send_task('worker.fibonacci', args=[n])
    redis = aioredis.from_url('redis://redis:6379', encoding='utf-8', decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe('task_updates')

    async def event_stream():
        task_completed = False
        while not task_completed:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                task_id, update = message['data'].split(':')
                
                if task_id == task.id:
                    yield f"data: {update}\n\n"
                    if "Completed" in update:
                        task_completed = True
                        

    return StreamingResponse(event_stream(), media_type="text/event-stream")

