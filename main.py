from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Dict
import json
import datetime
import uuid

app = FastAPI(title="Realtime Chat")

users: Dict[str, Dict] = {}
messages: Dict[str, Dict] = {}
reactions: Dict[str, Dict[str, List]] = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[Dict] = []

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        color = users[username]["color"]
        self.active_connections.append({"websocket": websocket, "username": username, "color": color})

    def disconnect(self, websocket: WebSocket):
        self.active_connections = [c for c in self.active_connections if c["websocket"] != websocket]

    async def broadcast(self, message: dict):
        dead = []
        for conn in self.active_connections:
            try:
                await conn["websocket"].send_text(json.dumps(message))
            except Exception:
                dead.append(conn)
        for c in dead:
            self.active_connections.remove(c)

    def get_users(self):
        return [{"username": c["username"], "color": c["color"]} for c in self.active_connections]

    def get_count(self):
        return len(self.active_connections)

manager = ConnectionManager()

@app.post("/auth")
async def auth(data: dict):
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    color = data.get("color", "#7c3aed")

    if not username or not password:
        return JSONResponse({"success": False, "error": "Username and password are required"})
    if len(username) < 2 or len(username) > 20:
        return JSONResponse({"success": False, "error": "Username must be 2-20 characters"})
    if len(password) < 3:
        return JSONResponse({"success": False, "error": "Password must be at least 3 characters"})

    if username in users:
        if users[username]["password"] != password:
            return JSONResponse({"success": False, "error": "Incorrect password"})
        return JSONResponse({"success": True, "username": username, "color": users[username]["color"], "action": "login"})
    else:
        users[username] = {"password": password, "color": color}
        return JSONResponse({"success": True, "username": username, "color": color, "action": "register"})

@app.get("/")
async def root():
    with open("templates/index.html") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    if username not in users:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, username)
    color = users[username]["color"]
    now = lambda: datetime.datetime.now().strftime("%H:%M")

    await manager.broadcast({
        "type": "system",
        "message": f"{username} joined the chat",
        "users": manager.get_users(),
        "count": manager.get_count(),
        "time": now()
    })

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type", "message")

            if msg_type in ("message", "reply"):
                msg_id = str(uuid.uuid4())[:8]
                msg = {
                    "id": msg_id,
                    "type": msg_type,
                    "username": username,
                    "color": color,
                    "message": data.get("text", ""),
                    "time": now(),
                    "users": manager.get_users(),
                    "count": manager.get_count(),
                    "reactions": {}
                }
                if msg_type == "reply":
                    msg["reply_to"] = {
                        "username": data.get("reply_to_user", ""),
                        "message": data.get("reply_to_text", "")
                    }
                messages[msg_id] = msg
                reactions[msg_id] = {}
                await manager.broadcast(msg)

            elif msg_type == "reaction":
                msg_id = data.get("message_id", "")
                emoji = data.get("emoji", "")
                if msg_id in reactions:
                    if emoji not in reactions[msg_id]:
                        reactions[msg_id][emoji] = []
                    if username in reactions[msg_id][emoji]:
                        reactions[msg_id][emoji].remove(username)
                    else:
                        reactions[msg_id][emoji].append(username)
                    reactions[msg_id] = {k: v for k, v in reactions[msg_id].items() if v}
                    await manager.broadcast({
                        "type": "reaction_update",
                        "message_id": msg_id,
                        "reactions": reactions[msg_id],
                        "users": manager.get_users(),
                        "count": manager.get_count(),
                        "time": now()
                    })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast({
            "type": "system",
            "message": f"{username} left the chat",
            "users": manager.get_users(),
            "count": manager.get_count(),
            "time": now()
        })
