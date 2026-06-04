
# ⚡ Autonomous Cron Agent

Welcome to the **Autonomous Cron Agent**! This is a robust, Python-based intelligent background agent designed to run continuously on Hugging Face Spaces. It allows you to schedule tasks using standard cron syntax, which are then autonomously executed by the **DeepSeek API** via the Hugging Face `smolagents` framework.

## 🚀 Features

- **True Cron Parsing**: Reads and schedules your tasks exactly to the minute using standard `* * * * *` crontab syntax.
- **Autonomous AI Execution**: Uses the DeepSeek model (`deepseek-v4-flash`) and `CodeAgent` to dynamically translate your text commands into executable Python code on the fly.
- **Live Terminal UI**: Features a sleek, dark-mode web dashboard that streams internal logs and agent activity in real-time.
- **Never Sleeps**: Built-in self-pinging architecture keeps the Hugging Face Space awake 24/7 so your scheduled tasks are never missed.
- **Hot-Reloading**: Automatically reloads your instruction file every hour. Add new tasks on the fly via the Hugging Face web UI without having to reboot the container!

## ⚙️ Setup & Deployment

1. **Deploy to Hugging Face**: Push this repository to a Hugging Face **Docker Space**.
2. **Add your API Key**: Go to your Space Settings > Variables and Secrets and add your DeepSeek API Key as a secret named `DEEPSEEK_API_KEY`.
3. **Add Tasks**: Open `task.md` and write your tasks using cron syntax.
   
   *Example:*
   ```text
   0 1 * * * curl https://example.com/health
   ```

## 🛠️ How it works under the hood

1. **`app.py`**: A FastAPI server running `APScheduler` in the background. It reads `task.md`, schedules the cron jobs, serves the live terminal UI, and pings itself daily to prevent the Space from sleeping.
2. **`agent.py`**: Uses `smolagents` to spin up a Python `CodeAgent`. When a scheduled cron job triggers, this script passes the instruction to DeepSeek, which writes and runs the Python code needed to fulfill the prompt!
