from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
import os
from datetime import datetime

# .env-Datei erstellen siehe .env.example
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str

class UserCreate(BaseModel):
    username: str

class RoomCreate(BaseModel):
    name: str
    user_id: int

class MessageCreate(BaseModel):
    room_id: int
    text: str
    user_id: int
    username: str

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

if not BASE_URL or not API_KEY:
    raise ValueError("FEHLER: .env Datei fehlt oder ist unvollständig! Siehe .env.example")

# WebSocket-Verbindung speichern
active_connections = {}

# Räume laden
@app.get("/rooms")
async def get_rooms():
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{BASE_URL}/rooms",
            headers={"api-key": API_KEY}
        )
    return res.json()

# Erstellen von Räumen
@app.post("/rooms")
async def create_room(room: RoomCreate):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{BASE_URL}/rooms",
            json={
                "Roomname": room.name,
                "UserID": room.user_id
            },
            headers={"api-key": API_KEY}
        )
    return res.json()

# Nachrichten aus Räume laden
@app.get("/messages")
async def get_messages(RoomID: int):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{BASE_URL}/messages",
            params={"RoomID": RoomID},
            headers={"api-key": API_KEY}
        )
    return res.json()

# Wird nicht benutzt dient nur als test
# User erstellen
@app.post("/userv2")
async def create_user(user: UserCreate):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/user",
            json={"Username": user.username},
            headers={"api-key": API_KEY}
        )
    return response.json()

# Wird nicht benutzt dient nur als test
# User laden
@app.get("/users")
async def get_users():
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{BASE_URL}/user",
            headers={"api-key": API_KEY}
        )
    return res.json()

# Erstellt einen neuen User oder loggt einen bestehenden ein
@app.post("/user")
async def create_or_login_user(user: UserCreate):
    async with httpx.AsyncClient() as client:
        try:
            # alle existierenden User
            get_response = await client.get(
                f"{BASE_URL}/user",
                headers={"api-key": API_KEY}
            )

            if get_response.status_code == 200:
                existing_users = get_response.json()

                # Durchsuche die Liste nach dem Namen
                for existing_u in existing_users:
                    if existing_u.get("Name") == user.username:
                        print(f"Login: User '{user.username}' gefunden. ID: {existing_u.get('ID')}")
                        return {
                            "ID": existing_u.get("ID"),
                            "Name": existing_u.get("Name"),
                            "message": "User logged in successfully"
                        }

        except Exception as e:
            print(f"Fehler beim Abrufen der User-Liste: {e}")

        # Wenn User NICHT gefunden wurde -> Neu anlegen
        print(f"Register: User '{user.username}' nicht gefunden. Erstelle neu...")

        create_response = await client.post(
            f"{BASE_URL}/user",
            json={"Username": user.username},
            headers={"api-key": API_KEY}
        )
        return create_response.json()

# WebSocket Verbindung aufbauen
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    # WebSocket Verbindung akzeptieren
    await websocket.accept()

    # User zur aktiven Verbindungsliste hinzufügen
    if user_id not in active_connections:
        active_connections[user_id] = []
    active_connections[user_id].append(websocket)
    print(f"User {user_id} verbunden")

    try:
        # Endlosschleife um die Verbindung offen halten
        while True:
            data = await websocket.receive_text()
            print(f"Nachricht von User {user_id}: {data}")

    except WebSocketDisconnect:
        # User entfernen, wenn die Verbindung getrennt wurde
        if user_id in active_connections:
            active_connections[user_id].remove(websocket)
            if not active_connections[user_id]:
                del active_connections[user_id]
        print(f"User {user_id} getrennt")

# Nachricht speichern und broadcastet sie an alle verbundenen WebSocket-Clients
@app.post("/message")
async def send_message(message: MessageCreate):
    # An API senden (Datenbank speichern)
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{BASE_URL}/messages",
            json={
                "RoomID": message.room_id,
                "UserID": message.user_id,
                "Message": message.text
            },
            headers={"api-key": API_KEY}
        )
    # Prüfen ob Speichern erfolgreich war
    if res.status_code == 200 or res.status_code == 201:

        formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Broadcast an alle aktiven WebSockets
        broadcast_data = {
            "RoomID": message.room_id,
            "UserID": message.user_id,
            "Name": message.username,
            "Text": message.text,
            "Time": formatted_time
        }

        # Durch alle verbundenen User
        for user_id, connections in active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(broadcast_data)
                except Exception as e:
                    print(f"Fehler beim Senden an {user_id}: {e}")

        return {"status": "success", "data": broadcast_data}
    else:
        # Fehlerbehandlung wenn API streikt
        return {"status": "error", "details": res.text}