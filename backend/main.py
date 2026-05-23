from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
import os

app = FastAPI(title="Life OS Backend - Antigravity Engine")

DB_FILE = "state.json"

def load_state():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {
        "user": {"name": "MASTER", "level": 22},
        "missions": [
            {"id": 1, "title": "Physical Threshold", "progress": 65, "status": "active"},
            {"id": 2, "title": "Cognitive Expansion", "progress": 30, "status": "active"},
        ],
        "knowledge_cards": [
            {"id": 1, "q": "What is the habit loop?", "a": "Cue -> Routine -> Reward", "interval": 3},
        ]
    }

def save_state(state):
    with open(DB_FILE, "w") as f:
        json.dump(state, f, indent=4)

state = load_state()

class Mission(BaseModel):
    id: int
    title: str
    progress: int
    status: str

@app.get("/api/status")
async def get_status():
    return {"status": "HERMES ONLINE", "operator": state["user"]["name"]}

@app.get("/api/missions")
async def get_missions():
    return state["missions"]

@app.post("/api/missions/{mission_id}/complete")
async def complete_mission(mission_id: int):
    global state
    for m in state["missions"]:
        if m["id"] == mission_id:
            m["progress"] = 100
            save_state(state)
            return {"status": "Mission Completed", "mission": m}
    raise HTTPException(status_code=404, detail="Mission not found")

@app.get("/api/knowledge")
async def get_knowledge():
    return state["knowledge_cards"]

@app.post("/api/knowledge/rate")
async def rate_card(card_id: int, rating: int):
    global state
    for c in state["knowledge_cards"]:
        if c["id"] == card_id:
            # Simple SRS logic: increase interval based on rating
            c["interval"] += (rating - 3)
            save_state(state)
            return {"status": "Card Updated", "new_interval": c["interval"]}
    raise HTTPException(status_code=404, detail="Card not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
