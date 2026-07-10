# HCP CRM — Handoff

## Current State
- **Backend:** DeepSeek provider active (`LLM_PROVIDER=deepseek` in `.env`). Backend runs on port 8000 via uvicorn.
- **Frontend:** Vite dev server on port 5173.
- **MySQL:** Running on port 3306 (not 3307).
- **Workspace:** `C:\Users\shado\Downloads\hcp-crm`

## Key Files
| File | Purpose |
|------|---------|
| `backend/agent/graph.py` | LangGraph agent, provider switch logic |
| `backend/agent/tools.py` | Tool functions (log_interaction, etc.) |
| `backend/main.py` | FastAPI endpoints, `_extract_form_state` |
| `backend/.env` | API keys + provider config |
| `frontend/src/components/StructuredForm.jsx` | Form component |
| `frontend/src/components/ChatInterface.jsx` | Chat component |
| `frontend/src/components/LogInteractionScreen.jsx` | Tab layout |
| `frontend/src/store/interactionSlice.js` | Redux state |

## Current Capabilities
- ✅ Chat logs interactions via DeepSeek (warm NL, no tables)
- ✅ Structured form auto-populates from chat (via `formState`)
- ✅ Structured form POSTs directly to `/api/interactions` (bypasses LLM)
- ✅ Groq provider works but rate-limited (free tier: 100K tokens/day)
- ✅ Groq→DeepSeek switch by changing `LLM_PROVIDER` in `.env` + restart

## Known Issues
- MySQL port: backend expects 3307, but MySQL runs on 3306 — need to update `backend/database.py` `DATABASE_URL` to `3306`
- Groq rate limit (~99K/100K tokens) — needs ~9min cooldown or upgrade

## Startup Order
1. MySQL (already running on 3306)
2. `cd backend && source venv/Scripts/activate && python -m uvicorn main:app --host 0.0.0.0 --port 8000`
3. `cd frontend && npm run dev` (port 5173)

## Last Tested
- Backend health: ✅
- DeepSeek chat + interaction logging + formState: ✅
- Form auto-populate in browser: pending refresh to confirm

## Links
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs
