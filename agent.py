import os
import datetime
from smolagents import CodeAgent, OpenAIServerModel

def execute_instruction(instruction: str):
    print(f"[{datetime.datetime.now()}] Executing instruction: {instruction}")
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: DEEPSEEK_API_KEY is not set.")
        return

    model = OpenAIServerModel(
        model_id="deepseek-v4-flash",
        api_base="https://api.deepseek.com",
        api_key=api_key
    )

    agent = CodeAgent(
        tools=[],
        model=model,
        additional_authorized_imports=["requests", "datetime", "json"]
    )

    try:
        result = agent.run(f"Execute the following instruction autonomously. Use python tools if needed.\n\nInstruction: {instruction}")
        print(f"Instruction executed successfully. Result:\n{result}")
        
        with open("agent_log.txt", "a") as f:
            f.write(f"--- {datetime.datetime.now()} ---\nInstruction: {instruction}\nResult: {result}\n\n")
            
    except Exception as e:
        print(f"Error executing instruction: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    execute_instruction("Test instruction")
