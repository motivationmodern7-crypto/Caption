from groq import Groq

client = Groq(api_key="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")

def convert_to_roman(text):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
             "role": "system",
"content": """
You are an expert in Urdu, Arabic, Naat, Hamd and Islamic poetry.

Your job:

Correct transcription mistakes.
Convert the corrected text into natural Roman Urdu.
Keep Islamic names and terms correct.

Rules:

Return ONLY Roman Urdu.
No explanations.
No notes.
No quotes.
No extra text.
"""
},
{
"role": "user",
"content": f"""
Correct and convert this text to Roman Urdu.

Example:

Input:
دارِ نبی پر یہ عمر بیتے

Output:
Dar-e-Nabi Par Yeh Umar Beete

Text:
{text}
"""
}
            ],
            temperature=0
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Groq Error:", e)
        return text