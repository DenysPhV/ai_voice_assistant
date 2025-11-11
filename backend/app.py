#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import shutil, os
import uuid
import uvicorn

from datetime import datetime
from typing import List
from pydantic import BaseModel
from bson import ObjectId
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from utils.speech_to_text import speech_to_text
from utils.ai_processor import process_query, load_ai_model
from utils.text_to_speech import text_to_speech
from utils.db_connector import connect_to_mongo, close_mongo_connection, get_conversations_collection

# ‼️ НОВИЙ 'lifespan' менеджер ‼️
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Код, що виконується ПІД ЧАС СТАРТУ ---
    print("Застосунок запускається...")
    
    # 1. Підключаємось до БД (ваш старий 'startup_db')
    connect_to_mongo()
    db = connect_to_mongo()
    await db["conversations"].create_index("user_id")
    await db["conversations"].create_index([("timestamp", -1)])
    print("✅ Підключення до БД встановлено.")
    
    # 2. Завантажуємо AI-модель
    print("⏳ Завантажуємо AI-модель... (це займе 6+ хвилин)")
    load_ai_model() # Викликаємо нашу синхронну функцію завантаження
    print("✅ AI-модель завантажена і готова до роботи.")
    
    yield
    
    # --- Код, що виконується ПІД ЧАС ЗУПИНКИ ---
    print("Застосунок зупиняється...")
    close_mongo_connection()
    print("✅ Підключення до БД закрито.")

app = FastAPI(lifespan=lifespan)

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


@app.post("/api/voice")
async def handle_voice(file: UploadFile, conversations=Depends(get_conversations_collection)):
    temp_path = None
    try:
        extension = os.path.splitext(file.filename)[1] or ".webm"
        safe_filename = f"{uuid.uuid4()}{extension}"
        temp_path = os.path.join("temp", safe_filename)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    
        # 1. Отримуємо текст від Whisper
        text = speech_to_text(temp_path)
        # 2. Отримуємо відповідь від AI (тепер з 'await', бо process_query - async)
        response = await process_query(text)
        # 3. Генеруємо аудіо
        audio_path = text_to_speech(response)
        # 4. Зберігаємо в БД
        doc = {
        "user_id": "anonymous",      
        "session_id": str(uuid.uuid4()),
        "timestamp": datetime.now(),
        "input_text": text,
        "response_text": response,
        "audio_path": f"/{audio_path}"
        }
        await conversations.insert_one(doc)
    
        return {
            "inputText": text, 
            "responseText": response, 
            "audio": f"/{audio_path}"
        }
    
    except Exception as e:
        # Повертаємо помилку, щоб фронтенд міг її обробити
        return {"error": str(e), "inputText": text if 'text' in locals() else "Помилка до STT"}
    
    finally:
        # Очищення тимчасового файлу, який завантажив користувач
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


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

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)