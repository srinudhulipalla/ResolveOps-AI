import os
import psycopg2
from pathlib import Path
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Force Python to load your .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_URL = os.getenv("DATABASE_URL")

# --- 🛠️ Define Database Tools ---

def check_inventory(employee_id: str) -> str:
    """Retrieves the list of hardware assigned to a specific employee ID."""
    print(f"\n[System Log] 🛠️ Agent is querying DB for inventory: {employee_id}")
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT asset_tag, device_type, model, status FROM inventory WHERE employee_id = %s", (employee_id,))
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not records:
            return f"No inventory found for employee {employee_id}."
            
        result = f"Inventory for {employee_id}:\n"
        for row in records:
            result += f"- {row[1]} (Model: {row[2]}, Tag: {row[0]}, Status: {row[3]})\n"
        return result
    except Exception as e:
        return f"Database error: {str(e)}"

def create_ticket(employee_id: str, issue_description: str) -> str:
    """Creates a new IT support ticket for an employee."""
    print(f"\n[System Log] 🛠️ Agent is creating a ticket in the DB for: {employee_id}")
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tickets (employee_id, issue_description, status) VALUES (%s, %s, %s) RETURNING ticket_id",
            (employee_id, issue_description, "Open")
        )
        ticket_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return f"Ticket successfully created. Ticket ID is #{ticket_id}."
    except Exception as e:
        return f"Database error: {str(e)}"

# --- 🤖 Define the Database Agent ---

database_agent = Agent(
    name="DatabaseAgent",
    model=os.getenv("MODEL_NAME", "gemini-3.1-flash-lite-preview"),
    tools=[check_inventory, create_ticket], # 🚨 Equip the agent with SQL powers
    instruction=(
        "You are an expert IT Service Desk Database Agent. Your job is to interact with the corporate "
        "PostgreSQL database to check employee hardware inventory and create IT support tickets. "
        "You MUST use your provided tools to look up or write information. Do not guess or invent data."
    )
)

db_runner = InMemoryRunner(agent=database_agent, app_name="ResolveOpsDatabase")
db_runner.auto_create_session = True

# --- 🧪 LOCAL MOCK TEST ---
if __name__ == "__main__":
    import uuid
    
    print("\n🔍 Booting up DatabaseAgent for a quick test...")
    session_id = str(uuid.uuid4()) # Keep the same session so it remembers the context
    
    # Test 1: Read Data (Querying)
    print("\n👤 You: Can you tell me what hardware is assigned to EMP-001?")
    test_msg_1 = types.Content(role="user", parts=[types.Part(text="Can you tell me what hardware is assigned to EMP-001?")])
    
    for event in db_runner.run(user_id="local_admin", session_id=session_id, new_message=test_msg_1):
        if event.content and event.content.parts and event.content.parts[0].text:
            print(f"🤖 Agent: {event.content.parts[0].text}")

    # Test 2: Write Data (Inserting)
    print("\n👤 You: Their laptop screen is flickering. Can you open a ticket for them?")
    test_msg_2 = types.Content(role="user", parts=[types.Part(text="Their laptop screen is flickering. Can you open a ticket for them?")])
    
    for event in db_runner.run(user_id="local_admin", session_id=session_id, new_message=test_msg_2):
        if event.content and event.content.parts and event.content.parts[0].text:
            print(f"🤖 Agent: {event.content.parts[0].text}")