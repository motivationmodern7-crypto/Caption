import os
import httpx
from groq import Groq

# Sahi environment variable name: GROQ_API_KEY
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
    http_client=httpx.Client(proxies=None)
)

def convert_to_roman(text):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert in Roman Urdu."},
                {"role": "user", "content": f"Convert the following text to Roman Urdu: {text}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Groq Romanization Error:", e)
        return text
