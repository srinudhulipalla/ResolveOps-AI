import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# 1. Import your specialized sub-agents
from app.agents.policy_agent import policy_agent
from app.agents.database_agent import database_agent

# Force Python to load your .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 2. Define the Supervisor Agent using sub_agents
supervisor_agent = Agent(
    name="SupervisorAgent",
    model=os.getenv("MODEL_NAME", "gemini-3.1-flash-lite-preview"),
    sub_agents=[policy_agent, database_agent],  # 🚨 Corrected: Using sub_agents for proper delegation
    instruction=(
        "You are the central IT Service Desk Supervisor. Your job is to analyze the user's request "
        "and route it to the correct specialized agent to get the answer.\n\n"
        "- If the user asks about IT rules, VPNs, remote work, or information security, delegate to the PolicyAgent.\n"
        "- If the user asks about hardware inventory, employee devices, or needs to open a support ticket, delegate to the DatabaseAgent.\n\n"
        "Do not attempt to answer the question yourself. Always delegate to the appropriate sub-agent to retrieve the factual information before responding."
    )
)

supervisor_runner = InMemoryRunner(agent=supervisor_agent, app_name="ResolveOpsSupervisor")
supervisor_runner.auto_create_session = True

# --- 🧪 LOCAL MOCK TEST ---
if __name__ == "__main__":
    import uuid
    
    print("\n🔍 Booting up SupervisorAgent for a routing test...")
    session_id = str(uuid.uuid4()) 
    
    # Test 1: Route to Policy Agent (ChromaDB)
    print("\n👤 You: What are the rules for working from home?")
    test_msg_1 = types.Content(role="user", parts=[types.Part(text="What are the rules for working from home?")])
    
    for event in supervisor_runner.run(user_id="local_admin", session_id=session_id, new_message=test_msg_1):
        if event.content and event.content.parts and event.content.parts[0].text:
            print(f"🤖 Supervisor: {event.content.parts[0].text}")

    # Test 2: Route to Database Agent (PostgreSQL)
    print("\n👤 You: Can you check the inventory for EMP-002?")
    test_msg_2 = types.Content(role="user", parts=[types.Part(text="Can you check the inventory for EMP-002?")])
    
    for event in supervisor_runner.run(user_id="local_admin", session_id=session_id, new_message=test_msg_2):
        if event.content and event.content.parts and event.content.parts[0].text:
            print(f"🤖 Supervisor: {event.content.parts[0].text}")