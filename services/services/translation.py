from openai import OpenAI
import os

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = (f"You are a professional video subtitle and story translator. "
              f"Translate the following spoken dialogue from {source_lang} to {target_lang}. "
              f"Ensure the translation sounds natural when spoken aloud. Maintain the emotional context and tone.\n\n"
              f"Original text:\n{text}")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a precise, natural-sounding translator."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
