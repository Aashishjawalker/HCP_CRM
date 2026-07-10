from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    formState: Optional[Dict[str, Any]] = None


class TranscribeResponse(BaseModel):
    text: str


class InteractionBase(BaseModel):
    hcp_name: str
    interaction_type: str = "meeting"
    date: str = ""
    time: str = ""
    attendees: str = ""
    topics_discussed: str = ""
    sentiment: str = "neutral"
    materials_shared: str = ""
    notes: str = ""


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(BaseModel):
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    sentiment: Optional[str] = None
    materials_shared: Optional[str] = None
    notes: Optional[str] = None


class InteractionResponse(InteractionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HCPProfileBase(BaseModel):
    name: str
    specialization: str = ""
    hospital: str = ""
    city: str = ""
    phone: str = ""
    email: str = ""


class HCPProfileResponse(HCPProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
