import time
from typing import Dict, List
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

chat_rooms: Dict[str, List[dict]] = {}
online_users: Dict[str, float] = {}

class MessagePayload(BaseModel):
    room: str
    sender: str
    text: str

class HeartbeatPayload(BaseModel):
    username: str

@app.get("/")
def health_check():
    return {"status": "Online", "server_time": time.time()}

@app.post("/send")
def process_incoming_message(data: MessagePayload):
    room_id = data.room
    if room_id not in chat_rooms:
        chat_rooms[room_id] = []
    message_entry = {
        "sender": data.sender,
        "text": data.text,
        "timestamp": time.time()
    }
    chat_rooms[room_id].append(message_entry)
    if len(chat_rooms[room_id]) > 50:
        chat_rooms[room_id].pop(0)
    return {"success": True}

@app.get("/messages/{room}")
def fetch_room_logs(room: str, since: float = 0.0):
    if room not in chat_rooms:
        return {"messages": []}
    filtered_messages = [msg for msg in chat_rooms[room] if msg["timestamp"] > since]
    return {"messages": filtered_messages}

@app.post("/heartbeat")
def handle_user_heartbeat(data: HeartbeatPayload):
    current_epoch = time.time()
    online_users[data.username] = current_epoch
    active_now = [
        username for username, last_seen in online_users.items()
        if current_epoch - last_seen < 12.0
    ]
    return {"online_users": active_now}
