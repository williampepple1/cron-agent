import os
import requests
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from agent import execute_task
import uvicorn
from contextlib import asynccontextmanager

def ping_self():
    # Hugging Face sets SPACE_HOST for the public URL
    space_host = os.getenv("SPACE_HOST")
    if space_host:
        url = f"https://{space_host}/ping"
        try:
            print(f"Pinging self at {url} to stay alive...")
            response = requests.get(url, timeout=10)
            print(f"Ping response: {response.status_code}")
        except Exception as e:
            print(f"Error pinging self: {e}")
    else:
        try:
            print("Pinging self at localhost to stay alive...")
            requests.get("http://127.0.0.1:7860/ping", timeout=10)
        except Exception as e:
            pass

def daily_task():
    print("Triggering daily task from scheduler...")
    execute_task()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    # Ping every 10 minutes to prevent HF from putting space to sleep
    scheduler.add_job(ping_self, 'interval', minutes=10)
    
    # Run the agent task daily at midnight UTC
    scheduler.add_job(daily_task, 'cron', hour=0, minute=0)
    
    scheduler.start()
    
    # Optionally trigger task on startup for immediate testing
    # execute_task()
    
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Cron Agent is running."}

@app.get("/ping")
def ping():
    return {"status": "alive"}

@app.post("/trigger")
def trigger_manual():
    # Allows you to manually trigger the task without waiting for the cron schedule
    execute_task()
    return {"status": "Task triggered"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
