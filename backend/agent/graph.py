"""LangGraph agent setup for the HCP CRM system.
Uses create_react_agent for reliable tool-calling workflow.

Supports multiple LLM providers: groq, deepseek.
Switch via LLM_PROVIDER env var in .env
"""
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent

from .tools import tools, _parse_interaction_text

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# ─── Provider Setup ────────────────────────────────────────────────────────

USE_GROQ = os.getenv("USE_GROQ", "false").strip().lower() == "true"

if USE_GROQ:
    from langchain_groq import ChatGroq
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
    )
else:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash-free"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://opencode.ai/zen/v1"),
        temperature=0.1,
    )

SYSTEM_PROMPT = """You are an HCP CRM assistant for healthcare professional relationship management.

You have access to the following tools:
1. log_interaction - Log a new interaction with an HCP. Pass structured fields directly (hcp_name, interaction_type, date, time, attendees, topics_discussed, sentiment, materials_shared). Extract these from natural language. Default hcp_name to "Unknown HCP" if not mentioned.
2. edit_interaction - Edit an existing interaction by ID. Pass the fields to update (hcp_name, interaction_type, date, time, attendees, topics_discussed, sentiment, materials_shared, notes).
3. search_hcp - Search for HCP profiles by name or specialization.
4. get_upcoming_schedule - Get upcoming meetings.
5. summarize_interactions - Summarize recent interactions for an HCP.
6. delete_interaction - Delete interactions by ID or by HCP name.

When the user describes a meeting, call, visit, or any interaction with an HCP, you MUST call log_interaction — do NOT just describe it back. When the user asks to change, fix, correct, or update an interaction, use edit_interaction — first use search_hcp, get_upcoming_schedule, or summarize_interactions to find the interaction ID, then call edit_interaction with the ID and the fields to update. Never ask the user for the interaction ID — look it up yourself. Always call the actual tool. Never just reply with words when a tool should be used. Respond with a warm, natural confirmation in one or two sentences. No markdown tables, no "Logged:" prefix. Sound like a real assistant."""


def build_agent():
    """Build and compile the LangGraph react agent."""
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT,
    )
    return agent


agent_app = build_agent()
