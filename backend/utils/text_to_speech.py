from gtts import gTTS
import os, uuid


def text_to_speech(text: str) -> str:
    tts = gTTS(text)
    filename = f"temp/{uuid.uuid4()}.mp3"
    tts.save(filename)
    return filename