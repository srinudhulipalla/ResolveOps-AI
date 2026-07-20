import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
import chromadb
from pypdf import PdfReader

# Force Python to load your .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize the Vector Database (In-Memory for our Agent layer)
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="it_policies")

def setup_vector_database():
    """Reads PDFs, chunks the text, and stores them as mathematical vectors."""
    policies_dir = Path(__file__).parent.parent.parent / "policies"
    if not policies_dir.exists():
        print("⚠️ Policies directory not found.")
        return

    pdf_files = list(policies_dir.glob("*.pdf"))
    
    # Prevent re-loading if the DB is already populated
    if collection.count() > 0:
        return

    print(f"🔄 Processing {len(pdf_files)} PDFs into the Vector Database...")
    
    chunk_id = 0
    for pdf_path in pdf_files:
        reader = PdfReader(pdf_path)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue
            
            # Chunking strategy: split into roughly 150-word blocks
            words = text.split()
            chunk_size = 150
            
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                
                # Store the text, metadata (source file and page), and a unique ID
                collection.add(
                    documents=[chunk],
                    metadatas=[{"source": pdf_path.name, "page": page_num + 1}],
                    ids=[f"chunk_{chunk_id}"]
                )
                chunk_id += 1
                
    print(f"🎯 Successfully indexed {chunk_id} vector chunks in ChromaDB!\n")

# Run the ingestion pipeline when the agent boots
setup_vector_database()

# Define the Tool the AI will use to search the database
def search_policies(query: str) -> str:
    """Searches the corporate IT policies for answers."""
    print(f"\n[System Log] 🛠️ Agent is querying Vector DB for: '{query}'")
    
    # Retrieve the top 3 most relevant chunks based on the query
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    
    if not results['documents'][0]:
        return "No relevant policy information found."
        
    combined_results = ""
    for i, doc in enumerate(results['documents'][0]):
        metadata = results['metadatas'][0][i]
        combined_results += f"\n--- Source: {metadata['source']} (Page {metadata['page']}) ---\n{doc}\n"
        
    return combined_results

# Define the Specialized Policy Agent
policy_agent = Agent(
    name="PolicyAgent",
    model=os.getenv("MODEL_NAME", "gemini-3.1-flash-lite-preview"),
    tools=[search_policies], # 🚨 Give the agent its new search tool
    instruction=(
        "You are an expert IT Corporate Policy Assistant. Your job is to answer employee "
        "questions accurately. You MUST use the `search_policies` tool to look up information "
        "before answering. Do not invent answers. Base your response strictly on the tool's results. "
        "If the answer is not in the tool's results, politely state that you do not have that information."
    )
)

policy_runner = InMemoryRunner(agent=policy_agent, app_name="ResolveOpsPolicies")
policy_runner.auto_create_session = True

# --- 🧪 LOCAL MOCK TEST ---
if __name__ == "__main__":
    import uuid
    
    test_message = types.Content(
        role="user", 
        parts=[types.Part(text="Who is the President of the United States?")]
    )
    
    print("👤 You: Who is the President of the United States?")
    
    for event in policy_runner.run(
        user_id="local_admin", 
        session_id=str(uuid.uuid4()), 
        new_message=test_message
    ):
        if event.content and event.content.parts and event.content.parts[0].text:
            print(f"\n🤖 Agent: {event.content.parts[0].text}")