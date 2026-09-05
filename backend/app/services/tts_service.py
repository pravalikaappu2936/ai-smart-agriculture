import os
import tempfile
import edge_tts


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


# ============================================================
# Generate Speech
# ============================================================

async def generate_speech(text: str, language: str) -> str:
    """
    Convert text into speech using Microsoft Edge TTS.

    Returns:
        str: Path to the generated MP3 file.
    """

    # --------------------------------------------------------
    # Validate text
    # --------------------------------------------------------
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    text = text.strip()

    # --------------------------------------------------------
    # Normalize language
    # --------------------------------------------------------
    language = (language or "English").strip()

    # --------------------------------------------------------
    # Select voice
    # --------------------------------------------------------
    voice = VOICE_MAP.get(
        language,
        VOICE_MAP["English"]
    )

    # --------------------------------------------------------
    # Create temporary MP3 file
    # --------------------------------------------------------
    temp_file = tempfile.NamedTemporaryFile(
        mode="wb",
        suffix=".mp3",
        delete=False
    )

    output_path = temp_file.name
    temp_file.close()

    try:
        # ----------------------------------------------------
        # Create Edge TTS communication
        # ----------------------------------------------------
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice
        )

        # ----------------------------------------------------
        # Generate MP3
        # ----------------------------------------------------
        await communicate.save(output_path)

        # ----------------------------------------------------
        # Verify file was created
        # ----------------------------------------------------
        if not os.path.exists(output_path):
            raise RuntimeError("TTS audio file was not created")

        if os.path.getsize(output_path) == 0:
            raise RuntimeError("TTS generated an empty audio file")

        return output_path

    except Exception:
        # ----------------------------------------------------
        # Remove incomplete file if TTS fails
        # ----------------------------------------------------
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except OSError:
            pass

        raise