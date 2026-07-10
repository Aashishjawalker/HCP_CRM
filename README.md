# HCP CRM — AI-First Log Interaction Module

## Prerequisites (New Laptop Setup)

| Software | Download |
|----------|----------|
| **Python 3.11+** | https://python.org |
| **MySQL Server 8+** | https://dev.mysql.com/downloads/mysql/ (Workbench optional — GUI for browsing DB) |
| **Node.js 18+** | https://nodejs.org (includes npm) |
| **Git** | https://git-scm.com |

Note:
```
This repo comes with the inbuild API keys to save time and can use directly after installing
```

Verify installs:
```powershell
python --version
mysql --version
node --version
npm --version
git --version
```
## Features 
```
Can add Log
Can edit log
Can summirize log
Can show upcomming meetings
Can use audio files as input to fetch data
```

## Quick Start

### 1. Clone & Backend Setup
```powershell
git clone <repo-url> hcp-crm
cd hcp-crm\backend
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

### 2. Configure Environment
Copy your API keys into `backend\.env`: #if you have your own api keys
```
GROQ_API_KEY=gsk_...
USE_GROQ=false                   # false=DeepSeek, true=Groq
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://opencode.ai/zen/v1
DEEPSEEK_MODEL=deepseek-v4-flash-free
```

### 3. Create MySQL Database
Open MySQL CLI or Workbench and run:
```sql
CREATE DATABASE hcp_crm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Edit `backend\database.py` line 8 — replace `***` with your MySQL root password:
```python
"mysql+pymysql://root:YOUR_PASSWORD@127.0.0.1:3306/hcp_crm"
```

### 4. Start Backend
```powershell
cd backend
.\venv\Scripts\Activate # can skip this line if everything is installed in ur lapotp
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```
API: http://localhost:8000 · Docs: http://localhost:8000/docs

### 5. Start Frontend (new terminal)
```powershell
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

## Switch LLM Provider

Edit `backend\.env`:
- `USE_GROQ=false` → DeepSeek 
- `USE_GROQ=true` → Groq (default)

Restart backend after changing.

## Tech Stack

| Requirement | Status |
|-------------|--------|
| **Frontend:** React + Redux | ✅ Built (Vite) |
| **Backend:** Python FastAPI | ✅ Built |
| **AI Agent:** LangGraph | ✅ Built |
| **LLMs:** Groq (Llama 3.3), DeepSeek (v4 Flash) | ✅ Switchable via provider config |
| **Database:** MySQL | ✅ Configured |

## What's Done

### Backend (`backend/`)
- **FastAPI server** at port 8000 with CORS
- **LangGraph agent** with tools: `log_interaction`, `edit_interaction`, `search_hcp`, `get_upcoming_schedule`, `summarize_interactions`, `delete_interaction`
- **Database models:** `Interaction` and `HCPProfile` (SQLAlchemy + MySQL)
- **API endpoints:** POST `/api/chat`, GET/PUT/DELETE `/api/interactions`, GET `/api/hcps`, GET `/api/hcps/search`

### Frontend (`frontend/`)
- **React + Redux Toolkit** app (Vite)
- **Log Interaction Screen** with tab switching between Form and Chat
- **Structured Form** — all fields: HCP Name, Interaction Type, Date, Time, Attendees, Topics, Sentiment, Materials
- **Chat Interface** — sends messages to POST `/api/chat`, displays responses as chat bubbles
- **Auto-populate** — chat replies update the form fields via Redux

## Project Structure

```
hcp-crm/
├── backend/
│   ├── .env                  # API keys + USE_GROQ flag
│   ├── main.py               # FastAPI app + routes
│   ├── database.py           # SQLAlchemy + MySQL
│   ├── models.py             # Interaction, HCPProfile
│   ├── schemas.py            # Pydantic models
│   ├── agent/
│   │   ├── tools.py          # LangGraph tools
│   │   └── graph.py          # LangGraph agent + provider switch
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api/index.js
│   │   ├── store/
│   │   │   ├── index.js
│   │   │   └── interactionSlice.js
│   │   └── components/
│   │       ├── LogInteractionScreen.jsx
│   │       ├── StructuredForm.jsx
│   │       └── ChatInterface.jsx
│   └── package.json
└── README.md
```
