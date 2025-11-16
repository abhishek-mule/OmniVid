from ..celery_app import app
import time

@app.task
def add(x, y):
    # A simple example task
    return x + y

@app.task
def long_running_task(seconds):
    # Example of a long-running task
    time.sleep(seconds)
    return f"Slept for {seconds} seconds"
