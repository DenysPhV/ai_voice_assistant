# backend/utils/speech_to_text.py
import torch
# import numpy

torch._C.has_lapack = True

import whisper


def speech_to_text(audio_path: str) -> str:
    model = whisper.load_model("base", device="cuda")
    result = model.transcribe(audio_path,  language="uk", temperature=0)
    return result["text"]