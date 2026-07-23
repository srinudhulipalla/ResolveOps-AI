# 🛠️ ResolveOps AI

An enterprise-grade IT Service Desk Copilot powered by **Agentic AI** and **Retrieval-Augmented Generation (RAG)**.

ResolveOps acts as an autonomous Tier-1 support agent designed to answer corporate policy questions, query hardware inventory, and manage support tickets by combining document vector search with structured database tools.

---

## ✨ Key Features

* **Policy Q&A (RAG):** Context-aware answers strictly grounded in internal IT policy PDFs (Information Security, Remote Work, VPN) using **ChromaDB**.
* **IT Operations Tools:** Tool-calling agents capable of querying IT asset databases and managing ticket states in real time.
* **Unified Single-Server Architecture:** FastAPI handles both backend API routing and direct serving of the decoupled SPA frontend.
* **Vector DB Management:** Built-in administrative utility to dynamically parse, embed, and rebuild vector stores directly from the web interface.
* **Enterprise Tech Stack:** Powered by Google's Agent Development Kit (ADK) and Gemini models.

---

## 🏗️ Architecture & Tech Stack

* **AI Agent Framework:** Google Agent Development Kit (ADK)
* **LLM Engine:** Gemini latest models
* **Backend Framework:** Python 3.11+ / FastAPI / Uvicorn
* **Relational Database:** PostgreSQL (Hardware Inventory & Support Tickets)
* **Vector Store:** ChromaDB (Policy PDF Embeddings from Gemini Cloud)
* **Frontend:** Single Page Application (Vanilla HTML5 / Modern CSS / JavaScript)

---

## ⚙️ Local Setup & Prerequisites

### 1. System Requirements

Ensure you have the following installed on your machine:

* **Python 3.11+** (Added to system `PATH`)
* **PostgreSQL** (Running locally on default port `5432` or via cloud URL)
* **uv** (Fast Python package installer). Install via PowerShell if not present:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```



---

### 2. Environment Configuration

Clone the repository and navigate into the root directory:

```powershell
git clone https://github.com/srinudhulipalla/ResolveOps-AI.git
```

Create and activate a virtual environment using `uv`:

```powershell
uv venv
.\.venv\Scripts\activate
```

Install all required dependencies:

```powershell
uv pip install -r requirements.txt
```

---

### 3. Configure Environment Variables

Create a file named **`.env`** in the root directory of the project with the following configuration:

```env
# Gemini API Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here
MODEL_NAME=your_gemini_model_to_use

# PostgreSQL Connection String
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/resolveops_db
```

---

### 4. Initialize the Relational Database

Run the database setup script to create the necessary tables (`tickets`, `inventory`) and populate initial seed data into PostgreSQL:

```powershell
python app/database/db_setup.py
```

---

## 🚀 Running the Application

### Step 1: Start the Server

With your virtual environment active, run the Uvicorn development server:

```powershell
uvicorn app.main:app --reload --env-file .env
```

The application will start hosting at `http://127.0.0.1:8000/`.

---

### Step 2: Access the Copilot Interface

Open your web browser and navigate to:

👉 **`http://127.0.0.1:8000`**

*(FastAPI serves the frontend directly from this unified endpoint).*

---

### Step 3: First-Time Vector DB Ingestion

Upon the first launch, the local ChromaDB vector store needs to ingest the policy documents:

1. Log into the web dashboard using test credentials found at `/api/login`.
2. Click the **🔄 Rebuild Vector DB** button in the dashboard interface.
3. The system will parse all PDFs in the `policies/` directory and generate the embeddings locally.

---

## 🧪 Interactive API Documentation

You can inspect and test all available REST endpoints and tool-calling interfaces directly via FastAPI's built-in Swagger UI:

* **Swagger UI:** `http://127.0.0.1:8000/docs`
* **ReDoc:** `http://127.0.0.1:8000/redoc`