from faster_whisper import WhisperModel
from roman_converter import convert_to_roman

model = WhisperModel(
    "large-v3",
    device="cpu",
    compute_type="int8"
)

def transcribe_video(video_path):

    segments, info = model.transcribe(
        video_path,
        beam_size=10,
        word_timestamps=True,
        task="transcribe",
        language="ur"
    )

    print("Detected Language:", info.language)

    results = []

    for segment in segments:

        original_text = segment.text.strip()

        roman_text = convert_to_roman(original_text)

        roman_words = roman_text.split()

        words = []

        if segment.words:

            for i, word in enumerate(segment.words):

                if i < len(roman_words):
                    display_word = roman_words[i]
                else:
                    continue

                words.append({
                    "word": display_word,
                    "start": round(word.start, 2),
                    "end": round(word.end, 2)
                })

        results.append({
            "text": roman_text,
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "words": words
        })

    return results
