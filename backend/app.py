#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import shutil, os
import uuid

from datetime import datetime
from typing import List
from pydantic import BaseModel
from bson import ObjectId

from fastapi import FastAPI, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from utils.speech_to_text import speech_to_text
from utils.ai_processor import process_query
from utils.text_to_speech import text_to_speech
from utils.db_connector import connect_to_mongo, close_mongo_connection, get_conversations_collection


app = FastAPI()
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConversationOut(BaseModel):
    id: str
    user_id: str
    session_id: str
    timestamp: str
    input_text: str
    response_text: str
    audio_path: str | None


if not os.path.exists("temp"):
    os.makedirs("temp")

app.mount("/temp", StaticFiles(directory="temp"), name="temp")

async def test():
    db = connect_to_mongo()
    print(await db.list_collection_names())

@app.get("/")
async def root():
    return {"message": "AI Voice Assistant backend is running 🚀"}
    

@app.post("/api/voice")
async def handle_voice(file: UploadFile, conversations=Depends(get_conversations_collection)):
    try:
        temp_path = f"temp/{file.filename}"

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    
        # Розпізнавання мовлення
        text = speech_to_text(temp_path)
        # Обробка запиту GPT
        response = process_query(text)
        # Синтез голосової відповіді
        audio_path = text_to_speech(response)

        doc = {
        "user_id": "anonymous",           # або ідентифікатор користувача
        "session_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime(),
        "input_text": text,
        "response_text": response,
        "audio_path": f"/{audio_path}",  # або повний URL
        "meta": {"model": "mt5-base", "source": "local_whisper"}
        }
        
        res = await conversations.insert_one(doc)
    
        return {"text": response, "audio": f"/{audio_path}"}
    
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/history", response_model=List[ConversationOut])
async def get_history(limit: int = 20, conversations=Depends(get_conversations_collection)):
    cursor = conversations.find().sort("timestamp", -1).limit(limit)
    docs = await cursor.to_list(length=limit)
    results = []
    for d in docs:
        results.append({
            "id": str(d.get("_id")),
            "user_id": d.get("user_id"),
            "session_id": d.get("session_id"),
            "timestamp": d.get("timestamp").isoformat() if d.get("timestamp") else None,
            "input_text": d.get("input_text"),
            "response_text": d.get("response_text"),
            "audio_path": d.get("audio_path")
        })
    return results

@app.on_event("startup")
async def startup_db():
    connect_to_mongo()
    # опціонально: створити індекси
    db = connect_to_mongo()
    await db["conversations"].create_index("user_id")
    await db["conversations"].create_index([("timestamp", -1)])

@app.on_event("shutdown")
async def shutdown_db():
    close_mongo_connection()

# dependency для отримання колекції
def get_conversations_collection():
    db = connect_to_mongo()
    return db["conversations"]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)