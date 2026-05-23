from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
import base64

app = FastAPI()

# --- Configuration from Vercel Env Vars ---
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USER = os.environ.get("GITHUB_USER", "nit454")
VAULT_REPO = os.environ.get("VAULT_REPO", "hermes-zettelkasten")
API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{VAULT_REPO}/contents"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# --- GitHub Memory Helpers ---
def read_vault_file(path):
    url = f"{API_URL}/{path}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        content_b64 = res.json()["content"]
        return base64.b64decode(content_b64).decode("utf-8")
    return None

def write_vault_file(path, content, message="Updated by Hermes Life OS"):
    url = f"{API_URL}/{path}"
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None
    
    data = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8")
    }
    if sha: data["sha"] = sha
    
    res = requests.put(url, headers=headers, json=data)
    return res.status_code == 200

# --- Models ---
class ChatRequest(BaseModel):
    message: str

# --- Endpoints ---
@app.get("/api/status")
async def get_status():
    # We check if the vault is accessible to confirm "Online" status
    if read_vault_file("BOOT.md") or read_vault_file("README.md"):
        return {"status": "NEURAL SYNC ACTIVE", "operator": "MASTER"}
    return {"status": "SYNCING...", "operator": "MASTER"}

@app.get("/api/missions")
async def get_missions():
    # We store missions in a JSON file inside the Obsidian vault!
    data = read_vault_file("system/lifeos_state.json")
    if data:
        import json
        return json.loads(data).get("missions", [])
    
    # Fallback / Initial Seed
    return [
        {"title": "Physical Threshold", "progress": 65, "status": "active"},
        {"title": "Cognitive Expansion", "progress": 30, "status": "active"},
    ]

@app.get("/api/knowledge")
async def get_knowledge():
    # DYNAMIC KNOWLEDGE: Read all .md files in the 'zettels' folder
    url = f"{API_URL}/zettels"
    res = requests.get(url, headers=headers)
    if res.status_code != 200: return []
    
    files = res.json()
    cards = []
    for f in files:
        if f["name"].endswith(".md"):
            content = read_vault_file(f["path"])
            # Simple Parser: Look for "Q: ..." and "A: ..." in the note
            if "Q:" in content and "A:" in content:
                q = content.split("Q:")[1].split("\n")[0].strip()
                a = content.split("A:")[1].split("\n")[0].strip()
                cards.append({"q": q, "a": a, "source": f["name"]})
    
    return cards if cards else [{"q": "Add 'Q:' and 'A:' to a note in /zettels to create a card", "a": "This is how the sync works!", "source": "system"}]

@app.post("/api/chat")
async def chat(request: ChatRequest):
    user_msg = request.message
    
    # 1. LOG TO OBSIDIAN: Save every chat to a daily log file in the vault
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_path = f"logs/{date_str}.md"
    
    current_log = read_vault_file(log_path) or f"# Chat Log - {date_str}\n\n"
    new_entry = f"\n**MASTER**: {user_msg}\n**HERMES**: Processing... \n---\n"
    write_vault_file(log_path, current_log + new_entry)

    # 2. GENERATE RESPONSE
    if "status" in user_msg.lower():
        response = "Neural Sync is active. Your Obsidian vault and Life OS are sharing a single consciousness."
    elif "mission" in user_msg.lower():
        response = "Checking your vault... your missions are synchronized. Keep pushing, Master."
    else:
        response = f"I have logged your command '{user_msg}' directly into your Obsidian vault under today's log. It is now part of your permanent record."
        
    return {"response": response}
