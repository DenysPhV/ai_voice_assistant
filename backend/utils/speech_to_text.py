import os
import openai


def speech_to_text(audio_path: str) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcriptions.create(
             model="whisper-1", file=audio_file )
    return transcript.text