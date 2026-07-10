"""
FastAPI application for HCP CRM.
"""
import os
import uuid
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import Interaction, HCPProfile
from schemas import (
    ChatRequest, ChatResponse, TranscribeResponse,
    InteractionCreate, InteractionResponse, InteractionUpdate,
    HCPProfileResponse,
)
from agent.graph import agent_app
from agent.tools import _parse_interaction_text

load_dotenv()

app = FastAPI(title="HCP CRM API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize database tables on startup."""
    init_db()


# ─── Helper ───────────────────────────────────────────────────────────────

def _to_hhmm(time_str: str) -> str:
    """Convert various time formats to HH:MM (24h) for <input type='time'>."""
    if not time_str:
        return ""
    t = time_str.strip().lower()
    # Already HH:MM
    import re
    if re.match(r'^([01]\d|2[0-3]):[0-5]\d$', t):
        return t
    # 3:00pm / 3:00 PM / 3:00 pm
    m = re.match(r'^(\d{1,2}):(\d{2})\s*(am|pm)?$', t)
    if m:
        h, mi, ap = int(m.group(1)), m.group(2), m.group(3)
        if ap == 'pm' and h < 12:
            h += 12
        elif ap == 'am' and h == 12:
            h = 0
        return f"{h:02d}:{mi}"
    # 3pm / 3 am / 3 PM
    m = re.match(r'^(\d{1,2})\s*(am|pm)$', t)
    if m:
        h, ap = int(m.group(1)), m.group(2)
        if ap == 'pm' and h < 12:
            h += 12
        elif ap == 'am' and h == 12:
            h = 0
        return f"{h:02d}:00"
    return time_str


def _snake_to_camel(d: Optional[dict]) -> Optional[dict]:
    """Convert snake_case dict keys to camelCase."""
    if not d:
        return d
    mapping = {
        "hcp_name": "hcpName",
        "interaction_type": "interactionType",
        "topics_discussed": "topicsDiscussed",
        "materials_shared": "materialsShared",
        "created_at": "createdAt",
        "updated_at": "updatedAt",
    }
    result = {}
    for k, v in d.items():
        new_key = mapping.get(k, k)
        # Normalize time to HH:MM so <input type='time'> displays it
        if new_key == "time":
            v = _to_hhmm(v)
        result[new_key] = v
    return result

def _extract_form_state(messages) -> Optional[dict]:
    """Extract form state from agent messages by looking for tool calls."""
    mapping = {
        "hcp_name": "hcpName",
        "interaction_type": "interactionType",
        "date": "date",
        "time": "time",
        "attendees": "attendees",
        "topics_discussed": "topicsDiscussed",
        "sentiment": "sentiment",
        "materials_shared": "materialsShared",
    }

    for msg in messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                name = tc.get("name")
                if name in ("log_interaction", "edit_interaction"):
                    args = tc.get("args", {})
                    form_state = {}
                    for old_key, new_key in mapping.items():
                        if old_key in args and args[old_key]:
                            form_state[new_key] = args[old_key]
                    if "sentiment" in form_state and form_state["sentiment"]:
                        form_state["sentiment"] = form_state["sentiment"].capitalize()
                    if "interactionType" in form_state and form_state["interactionType"]:
                        form_state["interactionType"] = form_state["interactionType"].capitalize()
                    return form_state if form_state else None
    return None


def _get_response_text(messages) -> str:
    """Get the last meaningful AI text response from messages."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
            return str(msg.content)
    # If no tool_call-free AI message, get the last AI message
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            return str(msg.content or "")
    return "Request processed successfully."


# ─── Chat Endpoint ────────────────────────────────────────────────────────

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Process a chat message through the LangGraph agent."""
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    # Run the agent
    try:
        result = agent_app.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config=config,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
    
    messages = result.get("messages", [])
    
    # Get the response text
    response_text = _get_response_text(messages)
    
    # Extract form state from tool calls
    form_state = _extract_form_state(messages)
    
    return ChatResponse(response=response_text, formState=_snake_to_camel(form_state))


# ─── Interaction Endpoints ────────────────────────────────────────────────

@app.get("/api/interactions", response_model=list[InteractionResponse])
def list_interactions(db: Session = Depends(get_db)):
    """List all interactions, ordered by most recent."""
    interactions = db.query(Interaction).order_by(Interaction.created_at.desc()).all()
    return interactions


@app.post("/api/interactions", response_model=InteractionResponse)
def create_interaction(data: InteractionCreate, db: Session = Depends(get_db)):
    """Create a new interaction directly (bypasses LLM agent)."""
    interaction = Interaction(
        hcp_name=data.hcp_name,
        interaction_type=data.interaction_type,
        date=data.date,
        time=data.time,
        attendees=data.attendees,
        topics_discussed=data.topics_discussed,
        sentiment=data.sentiment,
        materials_shared=data.materials_shared,
        notes=data.notes,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


@app.get("/api/interactions/{interaction_id}", response_model=InteractionResponse)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """Get a single interaction by ID."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@app.put("/api/interactions/{interaction_id}", response_model=InteractionResponse)
def update_interaction(interaction_id: int, update: InteractionUpdate, db: Session = Depends(get_db)):
    """Update an existing interaction."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interaction, field, value)
    
    db.commit()
    db.refresh(interaction)
    return interaction


@app.delete("/api/interactions/{interaction_id}")
def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """Delete an interaction by ID."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    db.delete(interaction)
    db.commit()
    return {"status": "deleted", "id": interaction_id}


# ─── HCP Endpoints ────────────────────────────────────────────────────────

@app.get("/api/hcps", response_model=list[HCPProfileResponse])
def list_hcps(db: Session = Depends(get_db)):
    """List all HCP profiles."""
    hcps = db.query(HCPProfile).order_by(HCPProfile.name).all()
    return hcps


@app.get("/api/hcps/search", response_model=list[HCPProfileResponse])
def search_hcps(q: str = Query("", description="Search query for HCP name or specialization"), db: Session = Depends(get_db)):
    """Search HCP profiles by name or specialization."""
    if not q:
        return []
    results = db.query(HCPProfile).filter(
        HCPProfile.name.ilike(f"%{q}%") |
        HCPProfile.specialization.ilike(f"%{q}%")
    ).all()
    return results


# ─── Transcription Endpoint ────────────────────────────────────────────────

MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25MB

@app.post("/api/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe an audio file using Groq Whisper."""
    if not file.filename or not file.filename.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg', '.webm', '.flac')):
        raise HTTPException(status_code=400, detail="Unsupported audio format. Use mp3, wav, m4a, ogg, webm, or flac.")

    contents = await file.read()
    if len(contents) > MAX_AUDIO_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max 25MB.")

    from groq import Groq
    import tempfile

    suffix = os.path.splitext(file.filename)[1] or ".webm"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        tmp.write(contents)
        tmp.close()

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        with open(tmp.name, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
            )
        return TranscribeResponse(text=transcription.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        os.unlink(tmp.name)


# ─── Health Check ─────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "message": "HCP CRM API is running"}


# ─── Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
