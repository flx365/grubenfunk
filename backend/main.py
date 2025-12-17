from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
import os

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

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")

if not BASE_URL or not API_KEY:
    raise ValueError("FEHLER: .env Datei fehlt oder ist unvollständig! Siehe .env.example")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/message")
def recieve_message(message: Message):
    print("Message recieved: ", message.text)
    return{"status": "ok", "recieved": message.text}

# Räume laden
@app.get("/rooms")
async def get_rooms():
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{BASE_URL}/rooms",
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

# User erstellen
@app.post("/user")
async def create_user(user: UserCreate):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/user",
            json={"Username": user.username},
            headers={"api-key": API_KEY}
        )
    return response.json()

# TODO: Test Zwecke noch nicht im Fronend implementiert
# http://localhost:8000/users
# User laden
@app.get("/users")
async def get_users():
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{BASE_URL}/user",
            headers={"api-key": API_KEY}
        )
    return res.json()