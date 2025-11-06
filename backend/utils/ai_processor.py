import os
import openai


def process_query(text: str) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")

    completion = openai.Chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": text}])
    
    return completion.choices[0].message.content
