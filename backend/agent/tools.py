"""
Agent tools for HCP CRM interaction management.
"""
import json
import re
from datetime import datetime, timedelta
from typing import Optional, Type

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Interaction, HCPProfile


def _parse_interaction_text(text: str) -> dict:
    """Use simple NLP heuristics to extract interaction fields from natural language.
    This serves as a fallback / supplement to LLM-based extraction.
    """
    result = {
        "hcp_name": "",
        "interaction_type": "meeting",
        "date": "",
        "time": "",
        "attendees": "",
        "topics_discussed": "",
        "sentiment": "neutral",
        "materials_shared": "",
    }

    text_lower = text.lower()

    # Extract interaction type
    type_map = {
        "meeting": ["meeting", "visit", "appointment"],
        "call": ["call", "phone", "telephone"],
        "email": ["email", "mail"],
        "lunch": ["lunch", "dinner", "breakfast", "meal"],
        "conference": ["conference", "seminar", "workshop", "webinar"],
        "presentation": ["presentation", "demo", "demonstration"],
    }
    for itype, keywords in type_map.items():
        if any(kw in text_lower for kw in keywords):
            result["interaction_type"] = itype
            break

    # Extract date - look for patterns like "today", "yesterday", "tomorrow", or date strings
    today = datetime.now()
    if "today" in text_lower:
        result["date"] = today.strftime("%Y-%m-%d")
    elif "yesterday" in text_lower:
        result["date"] = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    elif "tomorrow" in text_lower:
        result["date"] = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        # Try to find date patterns like "March 5" or "03/25" etc.
        date_patterns = [
            r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})",
            r"(\d{4})-(\d{1,2})-(\d{1,2})",
            r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s*(\d{4})?",
        ]
        for pat in date_patterns:
            m = re.search(pat, text_lower)
            if m:
                result["date"] = m.group(0)
                break

    # Extract time
    time_patterns = [
        r"(\d{1,2}):(\d{2})\s*(am|pm)",
        r"(\d{1,2})\s*(am|pm)",
    ]
    for pat in time_patterns:
        m = re.search(pat, text_lower)
        if m:
            result["time"] = m.group(0)
            break

    # Extract sentiment
    positive_words = ["great", "positive", "good", "excellent", "interested", "enthusiastic", "productive"]
    negative_words = ["negative", "bad", "poor", "uninterested", "concerned", "worried", "frustrated"]
    if any(w in text_lower for w in positive_words):
        result["sentiment"] = "positive"
    elif any(w in text_lower for w in negative_words):
        result["sentiment"] = "negative"

    # Extract HCP name - look for common name patterns
    # This is a simple heuristic; LLM will do better
    name_patterns = [
        r"(?:Dr\.|doctor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"(?:met with|saw|visited|called|emailed)\s+(?:Dr\.|doctor)?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    ]
    for pat in name_patterns:
        m = re.search(pat, text)
        if m:
            result["hcp_name"] = m.group(1).strip()
            break

    # Extract topics - look for phrases after "discussed" or "about"
    topic_match = re.search(r"(?:discussed|about|talked about|covered)\s+(.+?)(?:\.|,|$)", text)
    if topic_match:
        result["topics_discussed"] = topic_match.group(1).strip()

    # Extract materials
    material_match = re.search(r"(?:shared|gave|provided|left)\s+(.+?)(?:\.|,|$)", text)
    if material_match:
        result["materials_shared"] = material_match.group(1).strip()

    return result


@tool
def log_interaction(
    hcp_name: str = "",
    interaction_type: str = "meeting",
    date: str = "",
    time: str = "",
    attendees: str = "",
    topics_discussed: str = "",
    sentiment: str = "neutral",
    materials_shared: str = "",
) -> str:
    """Log a new HCP interaction. Provide as many structured fields as possible.
    
    Args:
        hcp_name: Name of the HCP.
        interaction_type: Type (meeting, call, email, lunch, conference, presentation).
        date: Date of interaction (YYYY-MM-DD or descriptive).
        time: Time of interaction.
        attendees: Who attended.
        topics_discussed: What was discussed.
        sentiment: Overall sentiment (positive, neutral, negative).
        materials_shared: Any materials shared.
    
    Returns:
        A confirmation message with the details.
    """
    db: Session = SessionLocal()
    try:
        interaction = Interaction(
            hcp_name=hcp_name or "Unknown HCP",
            interaction_type=interaction_type,
            date=date,
            time=time,
            attendees=attendees,
            topics_discussed=topics_discussed,
            sentiment=sentiment,
            materials_shared=materials_shared,
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        
        # Also try to ensure the HCP exists in profiles
        if hcp_name:
            existing = db.query(HCPProfile).filter(
                HCPProfile.name.ilike(f"%{hcp_name}%")
            ).first()
            if not existing:
                hcp = HCPProfile(name=hcp_name)
                db.add(hcp)
                db.commit()
        
        response = (
            f"✅ Interaction logged successfully (ID: {interaction.id}).\n"
            f"**HCP**: {interaction.hcp_name}\n"
            f"**Type**: {interaction.interaction_type}\n"
            f"**Date**: {interaction.date}\n"
            f"**Time**: {interaction.time}\n"
            f"**Topics**: {interaction.topics_discussed or 'N/A'}\n"
            f"**Sentiment**: {interaction.sentiment}\n"
            f"**Materials**: {interaction.materials_shared or 'N/A'}"
        )
        return response
    finally:
        db.close()


@tool
def edit_interaction(
    interaction_id: int,
    hcp_name: Optional[str] = None,
    interaction_type: Optional[str] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
    attendees: Optional[str] = None,
    topics_discussed: Optional[str] = None,
    sentiment: Optional[str] = None,
    materials_shared: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """Edit an existing interaction by its ID. Pass only the fields you want to update.
    
    Args:
        interaction_id: The ID of the interaction to edit.
        hcp_name: Update the HCP name.
        interaction_type: Update type (meeting, call, email, lunch, conference, presentation).
        date: Update date (YYYY-MM-DD).
        time: Update time (e.g. "2:00 PM").
        attendees: Update attendees list.
        topics_discussed: Update topics.
        sentiment: Update sentiment (positive, neutral, negative).
        materials_shared: Update materials shared.
        notes: Update additional notes.
        
    Returns:
        A confirmation message.
    """
    db: Session = SessionLocal()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return f"❌ Interaction with ID {interaction_id} not found."
        
        allowed_fields = {
            "hcp_name", "interaction_type", "date", "time", "attendees",
            "topics_discussed", "sentiment", "materials_shared", "notes"
        }
        
        updates = {}
        for field in allowed_fields:
            val = locals().get(field)
            if val is not None:
                updates[field] = val
        
        if not updates:
            return "ℹ️ No valid fields provided to update."
        
        for field, value in updates.items():
            setattr(interaction, field, value)
        
        db.commit()
        updated_fields = ", ".join(updates.keys())
        return f"✅ Interaction {interaction_id} updated: {updated_fields}"
    finally:
        db.close()


@tool
def search_hcp(query: str) -> str:
    """Search for HCP profiles by name or specialization.
    
    Args:
        query: Search term for HCP name or specialization.
        
    Returns:
        Formatted list of matching HCP profiles.
    """
    db: Session = SessionLocal()
    try:
        results = db.query(HCPProfile).filter(
            HCPProfile.name.ilike(f"%{query}%") | 
            HCPProfile.specialization.ilike(f"%{query}%")
        ).all()
        
        if not results:
            return f"ℹ️ No HCP profiles found matching '{query}'."
        
        lines = [f"**Found {len(results)} HCP(s):**"]
        for hcp in results:
            spec = f" - {hcp.specialization}" if hcp.specialization else ""
            hosp = f" @ {hcp.hospital}" if hcp.hospital else ""
            lines.append(f"• **{hcp.name}**{spec}{hosp} (ID: {hcp.id})")
        
        return "\n".join(lines)
    finally:
        db.close()


@tool
def get_upcoming_schedule() -> str:
    """Get a list of upcoming scheduled meetings and events.
    
    Returns:
        Formatted list of upcoming events.
    """
    db: Session = SessionLocal()
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        upcoming = db.query(Interaction).filter(
            Interaction.date >= today
        ).order_by(Interaction.date, Interaction.time).limit(10).all()
        
        if not upcoming:
            return "📅 No upcoming scheduled events found. You can log a new interaction!"
        
        lines = ["📅 **Upcoming Schedule:**"]
        for ev in upcoming:
            date_str = ev.date or "No date"
            time_str = ev.time or ""
            lines.append(f"• **{date_str}** {time_str} - {ev.interaction_type} with {ev.hcp_name} (ID: {ev.id})")
            if ev.topics_discussed:
                lines.append(f"  Topics: {ev.topics_discussed}")
        
        return "\n".join(lines)
    finally:
        db.close()


@tool
def summarize_interactions(hcp_name: str) -> str:
    """Summarize recent interactions with a specific HCP.
    
    Args:
        hcp_name: Name of the HCP to summarize interactions for.
        
    Returns:
        A summary of recent interactions.
    """
    db: Session = SessionLocal()
    try:
        interactions = db.query(Interaction).filter(
            Interaction.hcp_name.ilike(f"%{hcp_name}%")
        ).order_by(Interaction.date.desc()).limit(10).all()
        
        if not interactions:
            return f"ℹ️ No interactions found for HCP '{hcp_name}'."
        
        total = len(interactions)
        types = {}
        sentiments = {}
        topics = []
        
        for ix in interactions:
            types[ix.interaction_type] = types.get(ix.interaction_type, 0) + 1
            sentiments[ix.sentiment] = sentiments.get(ix.sentiment, 0) + 1
            if ix.topics_discussed:
                topics.append(ix.topics_discussed)
        
        lines = [
            f"📊 **Interaction Summary for {hcp_name}**",
            f"Total interactions: {total}",
            f"",
            f"**Types:** {', '.join(f'{k}: {v}' for k, v in types.items())}",
            f"**Sentiment trend:** {', '.join(f'{k}: {v}' for k, v in sentiments.items())}",
        ]
        
        if topics:
            lines.append(f"\n**Recent topics:**")
            for t in topics[:5]:
                lines.append(f"• {t}")
        
        lines.append(f"\n**Recent interactions:**")
        for ix in interactions[:5]:
            date_str = ix.date or "Unknown date"
            lines.append(f"• {date_str} - {ix.interaction_type} ({ix.sentiment})")
        
        return "\n".join(lines)
    finally:
        db.close()


@tool
def delete_interaction(interaction_id: Optional[int] = None, hcp_name: Optional[str] = None) -> str:
    """Delete interactions by ID or by HCP name.
    
    Provide either an interaction_id to delete a single interaction,
    or an hcp_name to delete all interactions for that HCP.
    
    Args:
        interaction_id: The ID of the interaction to delete (optional if hcp_name provided).
        hcp_name: Delete all interactions for this HCP name (optional if interaction_id provided).
        
    Returns:
        Confirmation message.
    """
    if interaction_id is None and hcp_name is None:
        return "❌ Please provide either an interaction_id or an hcp_name."
    
    db: Session = SessionLocal()
    try:
        if interaction_id is not None:
            interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
            if not interaction:
                return f"❌ Interaction with ID {interaction_id} not found."
            name = interaction.hcp_name
            db.delete(interaction)
            db.commit()
            return f"✅ Deleted interaction {interaction_id} ({name})."
        
        # Delete by HCP name
        interactions = db.query(Interaction).filter(
            Interaction.hcp_name.ilike(f"%{hcp_name}%")
        ).all()
        if not interactions:
            return f"ℹ️ No interactions found for '{hcp_name}'."
        count = len(interactions)
        for ix in interactions:
            db.delete(ix)
        db.commit()
        return f"✅ Deleted {count} interaction(s) for {hcp_name}."
    finally:
        db.close()


# Define the tool list for binding to the LLM
tools = [log_interaction, edit_interaction, search_hcp, get_upcoming_schedule, summarize_interactions, delete_interaction]
