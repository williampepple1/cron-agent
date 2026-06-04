import os
import re
import requests
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from agent import execute_instruction
import uvicorn
from contextlib import asynccontextmanager

def ping_self():
    space_host = os.getenv("SPACE_HOST")
    if space_host:
        url = f"https://{space_host}/ping"
        try:
            print(f"Pinging self at {url} to stay alive...")
            requests.get(url, timeout=10)
        except Exception as e:
            pass
    else:
        try:
            requests.get("http://127.0.0.1:7860/ping", timeout=10)
        except Exception as e:
            pass

def reload_tasks(scheduler):
    # Clear existing agent jobs
    for job in scheduler.get_jobs():
        if job.id != "ping_job" and job.id != "reload_job":
            scheduler.remove_job(job.id)

    print("Parsing task.md for cron jobs...")
    
    # Regex to match cron expression (5 parts) at start of string
    cron_pattern = re.compile(r'^((?:[0-9\*\,\-\/]+\s+){4}[0-9\*\,\-\/]+)\s+(.*)$')
    
    try:
        with open("task.md", "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("- "):
                    line = line[2:]
                
                match = cron_pattern.match(line)
                if match:
                    cron_expr = match.group(1).strip()
                    instruction = match.group(2).strip()
                    
                    try:
                        trigger = CronTrigger.from_crontab(cron_expr)
                        scheduler.add_job(execute_instruction, trigger=trigger, args=[instruction])
                        print(f"Scheduled: [{cron_expr}] -> {instruction}")
                    except ValueError as ve:
                        print(f"Invalid cron syntax '{cron_expr}': {ve}")
    except FileNotFoundError:
        print("task.md not found.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    
    # Self ping every 10 minutes
    scheduler.add_job(ping_self, 'interval', minutes=10, id="ping_job")
    
    # Load tasks on startup
    reload_tasks(scheduler)
    
    # Optionally, we can reload tasks dynamically every hour or day if task.md changes
    scheduler.add_job(lambda: reload_tasks(scheduler), 'interval', hours=1, id="reload_job")
    
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Cron Agent is running."}

@app.get("/ping")
def ping():
    return {"status": "alive"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
