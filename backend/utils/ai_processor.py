# utils/ai_processor.py
import re
import os
import asyncio
import torch
from transformers import pipeline
# from dotenv import load_dotenv


# load_dotenv()
# TOKEN_LLAMA = os.getenv("TOKEN_LLAMA")

# Ми більше не використовуємо BitsAndBytesConfig або AutoModelForCausalLM
model_name = "Qwen/Qwen2.5-1.5B-Instruct"
chat = None

def load_ai_model():
    """
    Завантажує модель Llama-3-8B-Instruct (Hugging Face).
    Оптимізовано для GPU / CPU.
    """
    global chat
    
    if chat is not None:
        print("✅ Модель Llama-3 вже завантажена.")
        return

    print(f"🚀 Завантаження моделі {model_name}...")
    
    try:
        # Спробуємо завантажити на GPU, якщо можливо
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        chat = pipeline(
            "text-generation",
            model=model_name,
            # token=TOKEN_LLAMA,
            device=device,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            max_new_tokens=350,
            do_sample=True,
            temperature=0.5,
            top_p=0.9
        )
        
        print(f"✅ Модель {model_name} готова (на пристрої: {device}).")
    
    except Exception as e:
        print(f"❌ Помилка завантаження {model_name}: {e}")
        print("Спроба завантажити на CPU...")
        chat = pipeline(
            "text-generation",
            model=model_name,
            device="cpu",
            torch_dtype=torch.float32
        )
        print("✅ Модель запущена на CPU.")


def llm_generate(prompt: str) -> str:
    """
    Викликає Qwen для генерації відповіді.
    Qwen НЕ використовує [INST], але працює чудово
    з системними інструкціями.
    """
    if chat is None:
        return "Помилка: Модель не завантажена."
    
    full_prompt = (
        "You are a university assistant AI. "
        "Respond concisely, accurately, and in Ukrainian.\n\n"
        f"### Запит студента:\n{prompt}\n\n### Відповідь:"
    )
    # TinyLlama використовує [INST]
    # outputs = chat(
    #     prompt,
    #     max_new_tokens=300,
    #     temperature=0.6,
    #     top_p=0.9,
    #     do_sample=True,
    # )
    output = chat(full_prompt)[0]["generated_text"]
    if "### Відповідь:" in output:
        output = output.split("### Відповідь:")[-1].strip()

    # Прибираємо повтор промпта
    response = output

    # Часто модель додає "Відповідь:" — прибираємо
    if response.lower().startswith("відповідь"):
        response = response.split(":", 1)[-1].strip()

    # Зайві пробіли та повтори
    response = re.sub(r'\s+', ' ', response).strip()

    return response or "Вибач, не зміг зрозуміти запит 😅" 


async def process_query(text: str) -> str:
    """
    Основна логіка обробки запиту користувача:
    - розклад занять
    - години прийому
    - або звичайний діалог
    """
    # ‼️ ВАЖЛИВО: Ми повинні імпортувати інструменти ТУТ, 
    # всередині async-функції, щоб уникнути помилок в 'lifespan'
    from .university_tools import get_schedule, get_office_hours

    if not text.strip():
        return "Вибач, я нічого не почув. Спробуй ще раз."
    
    text_lower = text.lower()
    # data_from_db = None
    
    # Розпізнавання запиту про розклад
    if "розклад" in text_lower or "пару" in text_lower:
        match = re.search(r'([0-9]{2,3}\s?[A-Za-zА-Яа-яМм])', text, re.IGNORECASE)

        if not match:
            return "Будь ласка, вкажіть номер групи. Наприклад: 'Розклад для 241М'."

        group = match.group(1).replace(" ", "")
        data = await get_schedule(group, "сьогодні")

        prompt = (
            f"Студент запитує розклад для групи {group}. "
            f"Ось дані з бази: {data}. "
            "Сформуй коротку відповідь українською."
        )
        return llm_generate(prompt)
        
    
    # Години прийому викладача
    if "прийому" in text_lower or "приймає" in text_lower:
        match = re.search(r"(прийому|приймає)\s+([А-Яа-яІіЇїЄє']+)", text_lower)

        if not match:
            return "Вкажіть прізвище викладача, щоб я міг знайти години прийому."

        professor = match.group(2)
        data = await get_office_hours(professor)

        prompt = (
            f"Студент запитує години прийому викладача {professor}. "
            f"Ось дані з бази: {data}. "
            "Сформуй коротку відповідь українською."
        )
        return llm_generate(prompt)

    # --- Звичайний чат ---
    default_prompt = (
        f"Студент задає питання: '{text}'. "
        "Відповідай чітко і по суті, як університетський асистент."
    )

    return llm_generate(default_prompt)