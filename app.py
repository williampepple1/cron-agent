import os
import re
import sys
import logging
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from agent import execute_instruction
import uvicorn
from contextlib import asynccontextmanager

# --- Logging Setup ---
LOG_FILE = "app.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Redirect stdout and stderr to the logger
class LoggerWriter:
    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message.strip() != "":
            self.level(message.strip())
            
    def flush(self):
        pass

sys.stdout = LoggerWriter(logger.info)
sys.stderr = LoggerWriter(logger.error)


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
    for job in scheduler.get_jobs():
        if job.id != "ping_job" and job.id != "reload_job":
            scheduler.remove_job(job.id)

    print("Parsing task.md for cron jobs...")
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
    scheduler.add_job(ping_self, 'cron', hour=0, minute=0, id="ping_job")
    reload_tasks(scheduler)
    scheduler.add_job(lambda: reload_tasks(scheduler), 'interval', hours=1, id="reload_job")
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

HTML_UI = """
<!DOCTYPE html>
<html>
<head>
    <title>Cron Agent Live Terminal</title>
    <style>
        body {
            background-color: #1e1e1e;
            color: #00ff00;
            font-family: 'Courier New', Courier, monospace;
            padding: 20px;
            margin: 0;
            height: 100vh;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
        }
        h2 {
            color: #ffffff;
            margin-top: 0;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
        }
        #terminal {
            flex-grow: 1;
            background-color: #000000;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #333;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
            font-size: 14px;
            line-height: 1.5;
        }
        .loading {
            color: #888;
        }
    </style>
</head>
<body>
    <h2>⚡ Cron Agent Terminal</h2>
    <div id="terminal"><span class="loading">Initializing connection to Hugging Face Space...</span></div>

    <script>
        const terminal = document.getElementById('terminal');
        let lastContent = "";
        
        // Helper to safely escape HTML to prevent XSS formatting issues
        function escapeHtml(unsafe) {
            return unsafe
                 .replace(/&/g, "&amp;")
                 .replace(/</g, "&lt;")
                 .replace(/>/g, "&gt;")
                 .replace(/"/g, "&quot;")
                 .replace(/'/g, "&#039;");
        }

        async function fetchLogs() {
            try {
                const response = await fetch('/api/logs');
                const data = await response.json();
                
                if (data.logs !== lastContent) {
                    lastContent = data.logs;
                    terminal.innerHTML = escapeHtml(data.logs);
                    terminal.scrollTop = terminal.scrollHeight;
                }
            } catch (error) {
                // Ignore transient errors so it doesn't clutter the UI
            }
        }

        setInterval(fetchLogs, 2000);
        fetchLogs();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def root():
    return HTML_UI

@app.get("/ping")
def ping():
    return {"status": "alive"}

@app.get("/api/logs")
def get_logs():
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            return {"logs": "".join(lines[-200:])}
    except FileNotFoundError:
        return {"logs": "Waiting for logs..."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
