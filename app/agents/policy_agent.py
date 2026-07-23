import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
import chromadb
from pypdf import PdfReader
import glob
from chromadb.utils.embedding_functions import GoogleGeminiEmbeddingFunction
from PyPDF2 import PdfReader

# Dynamically route the GOOGLE_API_KEY to GEMINI_API_KEY so ChromaDB can find it
if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

# 1. Setup Persistent Client
CHROMA_PATH = "./chroma_data"
client = chromadb.PersistentClient(path=CHROMA_PATH)

# 2. Configure the Google Gemini Cloud Embedding Function
# It automatically securely reads the GEMINI_API_KEY from your .env file
gemini_ef = GoogleGeminiEmbeddingFunction(
    model_name="gemini-embedding-001",
    task_type="RETRIEVAL_DOCUMENT"
)

def ingest_documents():
    """
    Reads PDFs from the policies folder, chunks them, and creates 
    cloud embeddings via Gemini ONLY when called explicitly.
    """
    policy_dir = "policies"
    if not os.path.exists(policy_dir):
        return {"status": "error", "message": "Policies folder not found."}

    # Delete existing collection if we are rebuilding to avoid duplicates
    try:
        client.delete_collection(name="it_policies")
    except Exception:
        pass # Collection didn't exist yet, which is fine

    # Create fresh collection enforcing the Gemini Embedding Engine
    collection = client.create_collection(
        name="it_policies",
        embedding_function=gemini_ef
    )
    
    documents = []
    metadatas = []
    ids = []
    
    # Read and chunk PDFs
    pdf_files = glob.glob(os.path.join(policy_dir, "*.pdf"))
    doc_id_counter = 1
    
    for pdf_path in pdf_files:
        try:
            reader = PdfReader(pdf_path)
            filename = os.path.basename(pdf_path)
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    # Basic chunking: split by paragraphs or just store page-by-page
                    # Here we store page-by-page for simplicity
                    documents.append(text.strip())
                    metadatas.append({"source": filename, "page": page_num + 1})
                    ids.append(f"doc_{doc_id_counter}")
                    doc_id_counter += 1
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")

    # Send chunks to Gemini for embedding and save locally in ChromaDB
    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Successfully embedded {len(documents)} chunks using Gemini Cloud.")
        return {"status": "success", "message": f"Embedded {len(documents)} document chunks."}
    
    return {"status": "warning", "message": "No text found to embed."}

def search_policies(query_text: str, n_results: int = 3) -> str:
    """
    Agent Tool: Retrieves policies using the Gemini Cloud embedding function.
    """
    try:
        collection = client.get_collection(
            name="it_policies", 
            embedding_function=gemini_ef
        )
        
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        if not results["documents"] or not results["documents"][0]:
            return "No relevant policy documents found in the database."
            
        # Format the retrieved chunks for the LLM context
        context = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            context.append(f"[Source: {meta['source']}, Page: {meta['page']}]\n{doc}\n")
            
        return "\n---\n".join(context)
        
    except Exception as e:
        return f"Error retrieving policies. The database might need to be rebuilt. Details: {e}"

# IMPORTANT: Notice there is NO function call here at the bottom of the file.
# The script will load without triggering the Gemini API.

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
        parts=[types.Part(text="Can you explain the rules for setting up a VPN?")]
    )
    
    print("👤 You: Can you explain the rules for setting up a VPN?")
    
    for event in policy_runner.run(
        user_id="local_admin", 
        session_id=str(uuid.uuid4()), 
        new_message=test_message
    ):
        if event.content and event.content.parts and event.content.parts[0].text:
            print(f"\n🤖 Agent: {event.content.parts[0].text}")