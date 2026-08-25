import edge_tts
import tempfile
import os


# ============================================================
# Supported languages and Microsoft Neural Voices
# ============================================================

VOICE_MAP = {
    "English": "en-IN-NeerjaNeural",
    "Hindi": "hi-IN-SwaraNeural",
    "Kannada": "kn-IN-SapnaNeural",
    "Telugu": "te-IN-ShrutiNeural",
    "Tamil": "ta-IN-PallaviNeural",
    "Malayalam": "ml-IN-SobhanaNeural",
    "Marathi": "mr-IN-AarohiNeural",
}


async def generate_speech(text: str, language: str) -> str:
    """
    Convert text into speech and return the generated MP3 path.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    voice = VOICE_MAP.get(language)

    if not voice:
        # Fallback to Indian English
        voice = VOICE_MAP["English"]

    # Create temporary MP3 file
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    output_path = temp_file.name
    temp_file.close()

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice
    )

    await communicate.save(output_path)

    return output_path