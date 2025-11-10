# backend/utils/text_to_speech.py
import uuid
from gtts import gTTS


def text_to_speech(text: str) -> str:
    filename = f"temp/{uuid.uuid4()}.webm"
    tts = gTTS(text=text, lang="uk") # або "en" якщо відповіді англійською
    tts.save(filename)
    return filename