# university_tools.py
import asyncio
import re

async def get_schedule(group: str, date: str) -> str:
    """
    Це "інструмент".
    У реальному світі ця функція підключається до SQL-бази чи API університету.
    Зараз ми імітуємо це.
    """
    print(f"[Tool Called] Fetching schedule for group {group} on {date}")
    
    # Імітуємо асинхронний запит до БД (наприклад, 0.5 секунди)
    await asyncio.sleep(0.5) 
    
    # Імітовані дані з БД
    mock_db_data = {
        "241М": "10:00 - Програмування (аудиторія 505), 12:00 - Математика (аудиторія 301)",
        "242": "08:30 - Історія (аудиторія 101)",
        "101": "09:00 - Фізика (аудиторія 222)",
    }
    
    # Нормалізуємо ім'я групи для пошуку
    normalized_group = group.upper().replace('M', 'М')
    normalized_group = re.sub(r'[^0-9A-ZМ]', '', group.upper())
    
    return mock_db_data.get(normalized_group, f"На жаль, розкладу для групи '{group}' не знайдено.")

async def get_office_hours(professor_name: str) -> str:
    """
    Ще один імітований інструмент для ТЗ.
    """
    print(f"[Tool Called] Fetching office hours for {professor_name}")
    await asyncio.sleep(0.2)
    
    mock_db_data = {
        "іванов": "Понеділок, 10:00 - 12:00 (каб. 301)",
        "петренко": "Вівторок, 14:00 - 16:00 (каб. 404)",
    }
    
    # Шукаємо прізвище
    for name_key, schedule in mock_db_data.items():
        if name_key in professor_name.lower():
            return schedule
            
    return f"На жаль, даних про години прийому для '{professor_name}' не знайдено."