import os
from groq import Groq

# Railway mein jo variable ka naam rakha hai (GROK_API_KEY), wo yahan likho
client = Groq(api_key=os.environ.get("GROK_API_KEY"),
    http_client=httpx.Client(proxies=None))

def convert_to_roman(text):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"Convert to Roman Urdu: {text}"}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Groq Error:", e) # Error check karne ke liye print zaroori hai
        return text
