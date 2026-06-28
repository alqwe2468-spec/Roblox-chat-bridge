from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

messages_db = {}
active_users = {}
# Tracks the last time a user sent a message to prevent spam
last_message_time = {}

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
    now = time.time()
    user_key = f"{msg.room}_{msg.sender}"
    
    # ANTI-SPAM: Check if user is sending faster than once every 2 seconds
    if user_key in last_message_time:
        time_passed = now - last_message_time[user_key]
        if time_passed < 2.0:
            raise HTTPException(status_code=429, detail="Spam detected! Slow down.")
            
    # Update their last message timestamp
    last_message_time[user_key] = now

    if msg.room not in messages_db:
        messages_db[msg.room] = []
    
    new_msg = {
        "sender": msg.sender,
        "text": msg.text,
        "timestamp": now
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
