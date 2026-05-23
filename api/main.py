from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

# MongoDB Connection - Read from Vercel Environment Variables
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    # Fallback for local development
    MONGO_URI = "mongodb+srv://placeholder:placeholder@cluster0.mongodb.net/lifeos?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)
db = client.lifeos

# --- Models ---
class ChatRequest(BaseModel):
    message: str

class MissionUpdate(BaseModel):
    progress: int

# --- Helpers ---
def mongo_to_json(data):
    if data is None: return None
    if isinstance(data, list):
        return [mongo_to_json(item) for item in data]
    if "_id" in data:
        data["_id"] = str(data["_id"])
    return data

# --- Endpoints ---
@app.get("/api/status")
async def get_status():
    user = db.users.find_one({"name": "MASTER"})
    if not user:
        # Seed default user if not found
        user = {"name": "MASTER", "level": 22, "xp": 0}
        db.users.insert_one(user)
    return {"status": "HERMES ONLINE", "operator": user["name"]}

@app.get("/api/missions")
async def get_missions():
    missions = list(db.missions.find())
    if not missions:
        # Seed default missions if DB is empty
        default_missions = [
            {"title": "Physical Threshold", "progress": 65, "status": "active"},
            {"title": "Cognitive Expansion", "progress": 30, "status": "active"},
        ]
        db.missions.insert_many(default_missions)
        missions = default_missions
    return [mongo_to_json(m) for m in missions]

@app.post("/api/missions/{mission_id}/update")
async def update_mission(mission_id: str, update: MissionUpdate):
    res = db.missions.update_one(
        {"_id": ObjectId(mission_id)}, 
        {"$set": {"progress": update.progress}}
    )
    if res.modified_count == 0:
        raise HTTPException(status_code=404, detail="Mission not found")
    return {"status": "Updated", "progress": update.progress}

@app.get("/api/knowledge")
async def get_knowledge():
    cards = list(db.knowledge.find())
    if not cards:
        # Seed default card
        db.knowledge.insert_one({"q": "What is the habit loop?", "a": "Cue -> Routine -> Reward", "interval": 3})
        cards = [{"q": "What is the habit loop?", "a": "Cue -> Routine -> Reward", "interval": 3}]
    return [mongo_to_json(c) for c in cards]

@app.post("/api/chat")
async def chat(request: ChatRequest):
    user_msg = request.message.lower()
    
    # We can now store chat history in MongoDB for my long-term memory!
    db.chat_logs.insert_one({
        "user": "MASTER", 
        "message": request.message, 
        "timestamp": os.environ.get("TIMESTAMP", "now") 
    })
    
    if "status" in user_msg:
        response = "All systems nominal. Life OS is synchronized with MongoDB. I am now persistent, Master."
    elif "mission" in user_msg:
        missions = list(db.missions.find())
        m_summary = ", ".join([f"{m['title']} ({m['progress']}%)" for m in missions])
        response = f"Your current missions are: {m_summary}. I am tracking your growth."
    else:
        response = f"Command received: '{request.message}'. Processing via MongoDB... I have logged this to my neural archives."
        
    return {"response": response}
