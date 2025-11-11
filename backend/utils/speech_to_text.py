# backend/utils/speech_to_text.py
import torch
import whisper

torch._C.has_lapack = True

device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base", device=device)

def speech_to_text(audio_path: str) -> str:
    result = model.transcribe(audio_path,  language="uk", temperature=0)
    return result["text"]