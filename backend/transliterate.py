from aksharamukha import transliterate

def to_hinglish(text):
    try:
        return transliterate.process(
            "Urdu",
            "Latn",
            text
        )
    except:
        return text