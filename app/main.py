import os
import uuid
import psycopg2
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.genai import types
from dotenv import load_dotenv

# Import the orchestrator and policy database tools
from app.agents.supervisor_agent import supervisor_runner
from app.agents.policy_agent import setup_vector_database, collection

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
DB_URL = os.getenv("DATABASE_URL")

app = FastAPI(title="ResolveOps AI API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🚨 NEW: Expose the policies folder as a static URL path
policies_path = Path(__file__).parent.parent / "policies"
app.mount("/static/policies", StaticFiles(directory=policies_path), name="policies")

# --- 🔒 Authentication ---
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/login")
def login(request: LoginRequest):
    """Simple hardcoded authentication for the prototype."""
    if request.username == "srinivas" and request.password == "Srinivas@123":
        return {"status": "success", "token": "resolve-auth-token-123"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# --- 🤖 Core AI Chat ---
class ChatRequest(BaseModel):
    message: str
    session_id: str = None

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Routes messages through the Supervisor Agent."""
    current_session = request.session_id or str(uuid.uuid4())
    user_message = types.Content(role="user", parts=[types.Part(text=request.message)])
    
    final_response = ""
    for event in supervisor_runner.run(
        user_id="web_user", 
        session_id=current_session, 
        new_message=user_message
    ):
        if event.content and event.content.parts and event.content.parts[0].text:
            final_response += event.content.parts[0].text
            
    return {"response": final_response, "session_id": current_session}

# --- 📄 Dashboard: Policies ---
@app.get("/api/policies")
def get_policies():
    """Scans the policies folder dynamically and returns a list of PDFs."""
    policies_dir = Path(__file__).parent.parent / "policies"
    if not policies_dir.exists():
        return []
    
    # Return just the filenames so the frontend can generate hyperlinks
    return [f.name for f in policies_dir.glob("*.pdf")]

@app.post("/api/rebuild-db")
def rebuild_db():
    """Wipes the existing ChromaDB vectors and re-indexes the PDFs."""
    existing_data = collection.get()
    if existing_data and existing_data['ids']:
        collection.delete(ids=existing_data['ids'])
    
    # Re-run the ingestion pipeline from policy_agent.py
    setup_vector_database()
    return {"status": "success", "message": "Vector database rebuilt successfully!"}

# --- 📊 Dashboard: Relational Data (PostgreSQL) ---
@app.get("/api/inventory")
def get_inventory():
    """Fetches all active hardware inventory records."""
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT asset_tag, employee_id, device_type, model, status FROM inventory")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{"asset_tag": r[0], "employee_id": r[1], "device_type": r[2], "model": r[3], "status": r[4]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tickets")
def get_tickets():
    """Fetches all IT support tickets."""
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT ticket_id, employee_id, issue_description, status, created_at FROM tickets")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # Dates are automatically serialized to ISO format by FastAPI
        return [{"ticket_id": r[0], "employee_id": r[1], "description": r[2], "status": r[3], "created_at": r[4]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))