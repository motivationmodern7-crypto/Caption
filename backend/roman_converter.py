import os
from groq import Groq

client = Groq(api_key=os.environ.get("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"))

def convert_to_roman(text):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"Convert to Roman Urdu: {text}"}]
        )
        return response.choices[0].message.content.strip()
    except:
        return text
