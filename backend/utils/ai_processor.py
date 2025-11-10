# ai_processor.py
import re
from transformers import pipeline

chat = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0")

def process_query(text: str) -> str:
    prompt = f"[INST] Ти — розмовний асистент. Відповідай коротко, українською мовою. Запит: {text} [/INST]"

    result   = chat(prompt, max_length=120, do_sample=True, temperature=0.5)[0]['generated_text']

    if '[/INST]' in result:
        result = result.split('[/INST]')[-1]

    result = re.sub(r'\[/?INST\]', '', result )          
    result = re.sub(r'^[^:]+:\s*', '', result) 
    result = re.sub(r'\s+', ' ', result).strip() 

    if result.lower().startswith(text.lower()): 
         result = result[len(text):].strip()

    return result or "Вибач, не зміг зрозуміти запит 😅"
