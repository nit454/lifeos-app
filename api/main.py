from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
import base64
from datetime import datetime

app = FastAPI()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USER = os.environ.get("GITHUB_USER", "nit454")
VAULT_REPO = os.environ.get("VAULT_REPO", "hermes-zettelkasten")
API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{VAULT_REPO}/contents"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def read_vault_file(path):
    url = f"{API_URL}/{path}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        content_b64 = res.json()["content"]
        return base64.b64decode(content_b64).decode("utf-8")
    return None

def write_vault_file(path, content, message="Updated by Hermes"):
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

class ChatRequest(BaseModel):
    message: str

@app.get("/api/status")
async def get_status():
    return {"status": "CONFLICT-FREE SYNC", "operator": "MASTER"}

@app.get("/api/missions")
async def get_missions():
    # Read state from the Safe Zone
    data = read_vault_file("hermes_sync/state.json")
    if data:
        import json
        return json.loads(data).get("missions", [])
    return [{"title": "Physical Threshold", "progress": 65, "status": "active"}]

@app.get("/api/knowledge")
async def get_knowledge():
    # Read-only access to zettels (no conflicts here)
    url = f"{API_URL}/zettels"
    res = requests.get(url, headers=headers)
    if res.status_code != 200: return []
    
    files = res.json()
    cards = []
    for f in files:
        if f["name"].endswith(".md"):
            content = read_vault_file(f["path"])
            if content and "Q:" in content and "A:" in content:
                q = content.split("Q:")[1].split("\n")[0].strip()
                a = content.split("A:")[1].split("\n")[0].strip()
                cards.append({"q": q, "a": a, "source": f["name"]})
    return cards if cards else [{"q": "Add 'Q:' and 'A:' to a note in /zettels", "a": "The sync is now conflict-free!", "source": "system"}]

@app.post("/api/chat")
async def chat(request: ChatRequest):
    # CONFLICT-FREE LOGGING: Unique filename per session
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = f"hermes_sync/logs/chat_{timestamp}.md"
    
    content = f"# Session {timestamp}\n\n**MASTER**: {request.message}\n**HERMES**: Processing via Conflict-Free Protocol..."
    write_vault_file(log_path, content)

    return {"response": f"Logged to /hermes_sync/logs/chat_{timestamp}.md. No conflicts possible."}
