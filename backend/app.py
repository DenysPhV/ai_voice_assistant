#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shutil

from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from utils.speech_to_text import speech_to_text
from utils.ai_processor import process_query
from utils.text_to_speech import text_to_speech


app = FastAPI()


app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)


@app.post("/api/voice")
async def handle_voice(file: UploadFile):
    temp_path = f"temp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    text = speech_to_text(temp_path)
    response = process_query(text)
    audio_path = text_to_speech(response)
    
    return {"text": response, "audio": audio_path}