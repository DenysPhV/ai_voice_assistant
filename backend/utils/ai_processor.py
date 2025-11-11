# utils/ai_processor.py
import re
import asyncio
import torch
from transformers import pipeline

# Ми більше не використовуємо BitsAndBytesConfig або AutoModelForCausalLM
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
chat = None

def load_ai_model():
    """
    Завантажує TinyLlama. 
    Ця модель достатньо мала, щоб поміститися у VRAM без 
    складної 4-бітної квантизації.
    """
    global chat
    
    if chat is not None:
        print("✅ Модель TinyLlama вже завантажена.")
        return

    print(f"Завантаження моделі {model_name}... Це займе 1-2 хвилини.")
    
    try:
        # Спробуємо завантажити на GPU, якщо можливо
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        chat = pipeline(
            "text-generation",
            model=model_name,
            device=device,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        )
        
        print(f"✅ Модель {model_name} готова (на пристрої: {device}).")
    
    except Exception as e:
        print(f"Помилка завантаження TinyLlama: {e}")
        print("Спроба завантажити на CPU...")
        # Якщо GPU не вдалося (наприклад, через ту саму помилку CUDA), 
        # гарантовано завантажуємо на CPU.
        chat = pipeline(
            "text-generation",
            model=model_name,
            device="cpu",
            torch_dtype=torch.float32
        )
        print(f"✅ Модель {model_name} готова (на пристрої: cpu).")


def llm_generate(prompt: str) -> str:
    """
    Викликає TinyLlama, використовуючи формат [INST].
    """
    if chat is None:
        return "Помилка: Модель TinyLlama не завантажена."

    # TinyLlama використовує [INST]
    result = chat(prompt, max_new_tokens=150, do_sample=True, temperature=0.7)[0]['generated_text']
    
    if '[/INST]' in result:
        result = result.split('[/INST]')[-1]

    result = result.strip()
    result = re.sub(r'\[\/?(INST|USER)\]', '', result).strip()
    result = re.sub(r'^[^:]+:\s*', '', result)
    result = re.sub(r'\s+', ' ', result).strip()

    if not result:
        return "Вибач, не зміг зрозуміти запит 😅"
        
    return result

async def process_query(text: str) -> str:
    """
    Оновлений процесор, який може використовувати інструменти.
    (Цей код залишається таким самим, але використовує [INST] промпт)
    """
    # ‼️ ВАЖЛИВО: Ми повинні імпортувати інструменти ТУТ, 
    # всередині async-функції, щоб уникнути помилок в 'lifespan'
    from .university_tools import get_schedule, get_office_hours

    if not text.strip():
        return "Вибач, я нічого не почув. Спробуй ще раз."

    text_lower = text.lower()
    
    schedule_intent = re.search(r'розк(лад|ат|ад|од)', text_lower)
    
    if schedule_intent:
        group_match = re.search(r'([0-9]{2,3}\s?[A-ZМ])', text, re.IGNORECASE) 
        if group_match:
            group_name = re.sub(r'\s', '', group_match.group(1))
            date = "сьогодні"
            
            # Викликаємо інструмент
            data_from_db = await get_schedule(group_name, date)
            
            # ‼️ ПОВЕРТАЄМОСЬ ДО [INST] ПРОМПТУ ‼️
            prompt = f"[INST] Ти — асистент університету з річним дочвідом. Надай відповідь на запит студента, використовуючи надані дані. Запит: '{text}', Дані з бази: '{data_from_db}' [/INST]"
            response = llm_generate(prompt)
            return response
        else:
            return "Я почув, що ви шукаєте розклад, але не зміг розпізнати номер групи. Спробуйте сказати чіткіше, наприклад: 'Розклад для 241М'."

    if "години прийому" in text_lower or "приймає" in text_lower:
        professor_match = re.search(r'(прийому|приймає)\s+([А-Яа-яІіЇї\']+)', text_lower)
        if professor_match:
            professor_name = professor_match.group(2)
            data_from_db = await get_office_hours(professor_name)
            
            prompt = f"[INST] Ти — асистент університету. Надай відповідь на запит студента, використовуючи надані дані. Запит: '{text}', Дані з бази: '{data_from_db}' [/INST]"
            response = llm_generate(prompt)
            return response
        else:
            return "Я можу надати години прийому, але, будь ласка, вкажіSь прізвище викладача."

    # --- Звичайний чат ---
    prompt = f"[INST] Ти — розмовний асистент. Відповідай коротко, українською мовою. Запит: {text} [/INST]"
    response = llm_generate(prompt)
    return response