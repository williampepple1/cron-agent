import os
import datetime
from openai import OpenAI

def execute_task():
    try:
        with open("task.md", "r") as f:
            task_content = f.read()
    except FileNotFoundError:
        print("task.md not found. Nothing to do.")
        return

    if not task_content.strip() or task_content.strip() == "# Daily Tasks":
        print("task.md is empty or default. Nothing to do.")
        return

    print(f"[{datetime.datetime.now()}] Executing task from task.md...")
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: DEEPSEEK_API_KEY is not set.")
        return
        
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    try:
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {"role": "system", "content": "You are an autonomous AI agent running as a cron job. Execute the user's daily tasks. Output the result of your execution."},
                {"role": "user", "content": f"Here is my task for today:\n\n{task_content}"}
            ]
        )
        # Fix model name just in case
        result = response.choices[0].message.content
        print(f"Task executed successfully. Result:\n{result}")
        
        with open("agent_log.txt", "a") as f:
            f.write(f"--- {datetime.datetime.now()} ---\n{result}\n\n")
            
    except Exception as e:
        print(f"Error executing task: {e}")

if __name__ == "__main__":
    # Allow manual testing
    from dotenv import load_dotenv
    load_dotenv()
    execute_task()
