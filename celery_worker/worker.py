import time
from celery import Celery
import redis
from typing import List
app = Celery('worker', broker='redis://redis:6379/0', backend='redis://redis:6379/0')
redis_client = redis.Redis(host='redis', port=6379, db=0)
import json


@app.task(bind=True)
def fibonacci(self, n: int) -> List[int]:
    f=[]
    def fib(n):
        if n <= 1:
            
            return n
        else:
            return fib(n - 1) + fib(n - 2)

    for i in range(n):
        f.append(fib(i))
        time.sleep(0.5) # Simulate a long computation
        redis_client.publish('task_updates', f'{self.request.id}: {json.dumps(f)}')
    f.append(fib(n))
    
    redis_client.publish('task_updates', f'{self.request.id}: Completed {json.dumps(f)}')
    
    return f