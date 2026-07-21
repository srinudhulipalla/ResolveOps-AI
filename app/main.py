import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.genai import types

# Import the orchestrator from our agents module
from app.agents.supervisor_agent import supervisor_runner

app = FastAPI(title="ResolveOps AI API")

# Configure CORS so your local HTML file is allowed to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the structure of the incoming HTTP request
class ChatRequest(BaseModel):
    message: str
    session_id: str = None

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Receives a message from the frontend, routes it through the Supervisor,
    and returns the AI's response.
    """
    # Use the provided session ID to maintain chat history, or create a new one
    current_session = request.session_id or str(uuid.uuid4())
    
    # Format the message for the ADK runner
    user_message = types.Content(
        role="user", 
        parts=[types.Part(text=request.message)]
    )
    
    # Run the supervisor and capture the output
    final_response = ""
    for event in supervisor_runner.run(
        user_id="web_user", 
        session_id=current_session, 
        new_message=user_message
    ):
        if event.content and event.content.parts and event.content.parts[0].text:
            final_response += event.content.parts[0].text
            
    return {
        "response": final_response, 
        "session_id": current_session
    }