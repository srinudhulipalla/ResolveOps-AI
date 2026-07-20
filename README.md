# 🛠️ ResolveOps AI

An intelligent IT Service Desk Copilot powered by Agentic AI. 

ResolveOps acts as a Tier-1 support agent designed to autonomously answer policy questions by querying corporate IT documentation. It utilizes a retrieval-augmented generation (RAG) architecture to provide accurate, context-aware answers based strictly on internal company policies.

## 🏗️ Architecture

- **Framework:** Google Agent Development Kit (ADK)
- **Backend:** Python / FastAPI
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Data Layer:** Document RAG (PDF processing)

## 📂 Project Structure

- `/app` - Core FastAPI server and AI agent routing logic.
- `/frontend` - Lightweight, decoupled client interface.
- `/policies` - Knowledge base containing standard IT policy PDFs (Information Security, Remote Work, VPN).

---



## ⚙️ Setup Instructions



### 1. Prerequisites

Ensure you have the following installed on your system:

- **Python 3.10+** (Ensure Python is added to your system PATH)
- **uv** (A fast Python package installer and resolver). Install it via terminal:
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
  ```

### 2. Environment Configuration

Clone or download this repository, open a terminal in the root directory, and create a secure virtual environment:

```powershell
uv venv
.\.venv\Scripts\activate
```

Install all required project dependencies from the requirements file:

```powershell
uv pip install -r requirements.txt
```

### 3. API Keys

Create a file named exactly `.env` in the root directory of the project and add your Google Gemini API key:

```powershell
GOOGLE_API_KEY=your_actual_key_here
MODEL_NAME=gemini-3.1-flash-lite-preview
```

## 🚀 Running the Application

**Step 1: Start the Backend Server** Keep your virtual environment active and run the FastAPI server to expose the AI endpoints:

```powershell
uvicorn app.main:app --reload --env-file .env
```

*Note: You can view the raw API documentation and test endpoints directly at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).*

**Step 2: Launch the Client Interface** Open your file explorer, navigate to the `frontend/` folder, and double-click `index.html`. It will open in your default web browser, allowing you to chat directly with the ResolveOps AI.

