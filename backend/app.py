#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import shutil, os

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from utils.speech_to_text import speech_to_text
from utils.ai_processor import process_query
from utils.text_to_speech import text_to_speech
from utils.db_connector import get_db


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

if not os.path.exists("temp"):
    os.makedirs("temp")

app.mount("/temp", StaticFiles(directory="temp"), name="temp")

@app.get("/")
async def root():
    return {"message": "AI Voice Assistant backend is running 🚀"}


@app.post("/api/voice")
async def handle_voice(file: UploadFile):
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

        db = get_db()
        db.dialogs.insert_one({
            "user_text": text,
            "ai_response": response
        })
    
        return {"text": response, "audio": f"/{audio_path}"}
    
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)