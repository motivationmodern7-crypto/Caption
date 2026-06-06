import os
import httpx # Yeh line bhi zaroori hai!
from groq import Groq

# Client initialization
client = Groq(
    api_key=os.environ.get("GROK_API_KEY"),
    http_client=httpx.Client(proxies=None)
)

def convert_to_roman(text):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert in Roman Urdu."},
                {"role": "user", "content": f"Convert to Roman Urdu: {text}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Groq Error:", e)
        return text
