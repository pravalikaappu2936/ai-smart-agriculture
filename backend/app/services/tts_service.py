import io
import edge_tts


# =========================================================
# TTS VOICES
# =========================================================

TTS_VOICES = {
    "English": "en-IN-NeerjaNeural",
    "Kannada": "kn-IN-SapnaNeural",
    "Hindi": "hi-IN-SwaraNeural",
    "Telugu": "te-IN-ShrutiNeural",
    "Tamil": "ta-IN-PallaviNeural",
    "Malayalam": "ml-IN-SobhanaNeural",
    "Marathi": "mr-IN-AarohiNeural",
}


# =========================================================
# NORMALIZE LANGUAGE
# =========================================================

def normalize_tts_language(language: str) -> str:

    if not language:
        return "English"

    language = language.strip().lower()

    for supported_language in TTS_VOICES:

        if language == supported_language.lower():
            return supported_language

    return "English"


# =========================================================
# GENERATE SPEECH
# =========================================================

async def generate_speech(
    text: str,
    language: str = "English"
) -> bytes:

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    text = text.strip()

    language = normalize_tts_language(language)

    voice = TTS_VOICES[language]

    print("=================================")
    print("TEXT TO SPEECH")
    print("Language:", language)
    print("Voice:", voice)
    print("=================================")

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate="+0%",
        volume="+0%",
        pitch="+0Hz"
    )

    audio_buffer = io.BytesIO()

    async for chunk in communicate.stream():

        if chunk["type"] == "audio":

            audio_buffer.write(
                chunk["data"]
            )

    audio_buffer.seek(0)

    audio = audio_buffer.read()

    if not audio:

        raise RuntimeError(
            "TTS service returned empty audio."
        )

    return audio