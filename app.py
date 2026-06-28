from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

app = FastAPI()

# UNLOCK CORS: This tells web browsers to allow requests from your HTML file
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all websites/local files to connect
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET and POST requests
    allow_headers=["*"],  # Allows Content-Type and custom headers
)

# Storage for messages and online players
messages_db = {}
active_users = {}

class Message(BaseModel):
    room: str
    sender: str
    text: str

class Heartbeat(BaseModel):
    username: str

@app.get("/")
def home():
    return {"status": "Online"}

@app.post("/send")
def send_message(msg: Message):
    if msg.room not in messages_db:
        messages_db[msg.room] = []
    
    new_msg = {
        "sender": msg.sender,
        "text": msg.text,
        "timestamp": time.time()
    }
    messages_db[msg.room].append(new_msg)
    return {"success": True}

@app.get("/messages/{room}")
def get_messages(room: str, since: float = 0.0):
    if room not in messages_db:
        return {"messages": []}
    
    filtered = [m for m in messages_db[room] if m["timestamp"] > since]
    return {"messages": filtered}

@app.post("/heartbeat")
def user_heartbeat(data: Heartbeat):
    active_users[data.username] = time.time()
    return {"success": True}

@app.get("/users")
def get_active_users():
    now = time.time()
    # Remove users who haven't sent a heartbeat in 25 seconds
    expired = [user for user, ts in active_users.items() if now - ts > 25]
    for user in expired:
        del active_users[user]
    return {"online_users": list(active_users.keys())}
