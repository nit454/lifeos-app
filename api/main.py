from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI()

# Since Vercel functions are stateless, for a production 'Life OS', 
# we would connect this to a MongoDB or Redis instance.
# For now, we use a 'Memory-State' that acts as a template.
# In a real scenario, these would be fetched from a DB via an API key.

state = {
    "user": {"name": "MASTER", "level": 22},
    "missions": [
        {"id": 1, "title": "Physical Threshold", "progress": 65, "status": "active"},
        {"id": 2, "title": "Cognitive Expansion", "progress": 30, "status": "active"},
    ],
    "knowledge_cards": [
        {"id": 1, "q": "What is the habit loop?", "a": "Cue -> Routine -> Reward", "interval": 3},
    ]
}

class ChatRequest(BaseModel):
    message: str

@app.get("/api/status")
async def get_status():
    return {"status": "HERMES ONLINE", "operator": state["user"]["name"]}

@app.get("/api/missions")
async def get_missions():
    return state["missions"]

@app.get("/api/knowledge")
async def get_knowledge():
    return state["knowledge_cards"]

@app.post("/api/chat")
async def chat(request: ChatRequest):
    # This is the bridge to the Hermes Brain.
    # In production, this would call the Hermes Agent API via a secure token.
    user_msg = request.message.lower()
    
    if "status" in user_msg:
        response = "All systems nominal. Life OS is synchronized. I am monitoring your progress, Master."
    elif "mission" in user_msg:
        response = "You have 2 active missions. Physical Threshold is at 65%. Push harder."
    else:
        response = f"Command received: '{request.message}'. Processing through the Antigravity Engine... I am online and awaiting your strategic direction."
        
    return {"response": response}
