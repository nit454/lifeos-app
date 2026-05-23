from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Life OS Backend - Antigravity Engine")

# Mock Database
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

class Mission(BaseModel):
    id: int
    title: str
    progress: int
    status: str

class KnowledgeCard(BaseModel):
    id: int
    q: str
    a: str
    interval: int

@app.get("/api/status")
async def get_status():
    return {"status": "HERMES ONLINE", "operator": state["user"]["name"]}

@app.get("/api/missions")
async def get_missions():
    return state["missions"]

@app.post("/api/missions/{mission_id}/complete")
async def complete_mission(mission_id: int):
    for m in state["missions"]:
        if m["id"] == mission_id:
            m["progress"] = 100
            return {"status": "Mission Completed", "mission": m}
    raise HTTPException(status_code=404, detail="Mission not found")

@app.get("/api/knowledge")
async def get_knowledge():
    return state["knowledge_cards"]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
