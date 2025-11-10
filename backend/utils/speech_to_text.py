import os
from openai import OpenAI


def speech_to_text(audio_path: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    with open(audio_path, "rb") as audio_file:

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        
    return transcript.text