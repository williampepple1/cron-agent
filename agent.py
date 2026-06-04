import os
import datetime
from smolagents import CodeAgent, OpenAIServerModel

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

    # Use OpenAIServerModel to connect to DeepSeek API
    model = OpenAIServerModel(
        model_id="deepseek-v4-flash",
        api_base="https://api.deepseek.com",
        api_key=api_key
    )

    # CodeAgent with access to the requests library
    agent = CodeAgent(
        tools=[],
        model=model,
        additional_authorized_imports=["requests", "datetime", "json"]
    )

    try:
        # We tell the agent to execute the instructions
        result = agent.run(f"Execute the following instructions. If you need to make web requests, use the `requests` library in python.\n\nInstructions:\n{task_content}")
        print(f"Task executed successfully. Result:\n{result}")
        
        with open("agent_log.txt", "a") as f:
            f.write(f"--- {datetime.datetime.now()} ---\n{result}\n\n")
            
    except Exception as e:
        print(f"Error executing task: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    execute_task()
