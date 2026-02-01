from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
import os
from datetime import datetime
import sqlite3

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

class MarkReadRequest(BaseModel):
    room_id: int
    user_id: int

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

if not BASE_URL or not API_KEY:
    raise ValueError("FEHLER: .env Datei fehlt oder ist unvollständig! Siehe .env.example")

# WebSocket-Verbindung speichern
active_connections = {}

# --- DATENBANK SETUP (SQLite) ---
DB_NAME = "local_cache.db"
@app.on_event("startup")
def startup_db():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS room_cursor (
                    user_id INTEGER,
                    room_id INTEGER,
                    last_read_msg_id INTEGER,
                    PRIMARY KEY (user_id, room_id)
                )
            """)
            conn.commit()
        print("SQLite Datenbank (synchron) initialisiert.")
    except Exception as e:
        print(f"Fehler beim Initialisieren der DB: {e}")


# --- API ---
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

@app.post("/rooms/mark_read")
async def mark_room_as_read(data: MarkReadRequest):
    async with httpx.AsyncClient() as client:
        # Alle Nachrichten des Raums laden
        messages = await api_fetch_messages(client, data.room_id)

        if messages is None:
            return {"status": "error", "details": "Could not fetch messages"}
        if not messages:
            return {"status": "success", "message": "No messages"}
        messages.sort(key=lambda x: x['MessageID'])

        # IDs ermitteln
        current_last_msg_id = messages[-1].get("MessageID")
        old_last_msg_id = db_get_last_read(data.user_id, data.room_id)

        # Abbruch, wenn nichts Neues
        if current_last_msg_id <= old_last_msg_id:
            return {"status": "success", "message": "Nothing new to mark"}

        # Lokal speichern
        db_update_last_read(data.user_id, data.room_id, current_last_msg_id)

        # Sync mit PHP API (Delta Logic)
        new_messages = [m for m in messages if m['MessageID'] > old_last_msg_id]

        if new_messages:
            for msg in new_messages:
                msg_id = msg.get('MessageID')

                # Check: Hat API das schon?
                already_read = await api_check_read_status(client, msg_id, data.user_id)

                # Wenn nicht, senden
                if not already_read:
                    await api_send_read_confirmation(client, data.user_id, msg_id)

    return {
        "status": "success",
        "last_read_id": current_last_msg_id,
        "synced_messages": len(new_messages)
    }

@app.get("/rooms/unread/last_message")
async def get_unread_rooms_last_message(user_id: int):
    unread_room_ids = []

    async with httpx.AsyncClient() as client:
        # Alle Räume laden
        rooms = await api_fetch_rooms(client)
        if not rooms:
            return {"status": "error", "details": "Could not load rooms"}

        # Durch Räume loopen
        for room in rooms:
            room_id = room["ID"]

            # Nachrichten holen
            messages = await api_fetch_messages(client, room_id)
            if not messages:
                continue
            messages.sort(key=lambda x: x['MessageID'])

            last_msg = messages[-1]
            last_msg_id = last_msg["MessageID"]

            # Eigene Nachrichten ignorieren
            if last_msg["UserID"] == user_id:
                continue

            # Lokalen Stand holen (SQLite)
            local_read_id = db_get_last_read(user_id, room_id)

            # Vergleich
            if last_msg_id > local_read_id:
                unread_room_ids.append(room_id)

    return {"unread_room_ids": unread_room_ids}


# Holt die letzte gelesene MessageID aus der lokalen DB
def db_get_last_read(user_id: int, room_id: int) -> int:
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT last_read_msg_id FROM room_cursor WHERE user_id = ? AND room_id = ?",
                (user_id, room_id)
            )
            row = cursor.fetchone()
            return row[0] if row else 0
    except Exception as e:
        print(f"DB Read Error: {e}")
        return 0

# Speichert die neue MessageID in der lokalen DB
def db_update_last_read(user_id: int, room_id: int, msg_id: int):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO room_cursor (user_id, room_id, last_read_msg_id) 
                VALUES (?, ?, ?)
            """, (user_id, room_id, msg_id))
            conn.commit()
    except Exception as e:
        print(f"DB Write Error: {e}")

# Lädt alle Räume von der PHP API
async def api_fetch_rooms(client: httpx.AsyncClient):
    res = await client.get(f"{BASE_URL}/rooms", headers={"api-key": API_KEY})
    if res.status_code == 200:
        return res.json()
    return []

# Lädt Nachrichten eines Raums. Gibt None zurück bei Fehler
async def api_fetch_messages(client: httpx.AsyncClient, room_id: int):
    res = await client.get(
        f"{BASE_URL}/messages",
        params={"RoomID": room_id},
        headers={"api-key": API_KEY}
    )
    if res.status_code == 200:
        return res.json()
    return None

# Prüft via API, ob der User die Nachricht schon gelesen hat
async def api_check_read_status(client: httpx.AsyncClient, msg_id: int, user_id: int) -> bool:
    res = await client.get(
        f"{BASE_URL}/readconfirmation",
        params={"MessageID": msg_id},
        headers={"api-key": API_KEY}
    )
    if res.status_code == 200:
        readers = res.json()
        # Prüfen ob UserID in der Liste ist
        return any(r.get('UserID') == user_id for r in readers)
    return False

# Sendet POST Request an API
async def api_send_read_confirmation(client: httpx.AsyncClient, user_id: int, msg_id: int):
    await client.post(
        f"{BASE_URL}/readconfirmation",
        json={"UserID": user_id, "MessageID": msg_id},
        headers={"api-key": API_KEY}
    )