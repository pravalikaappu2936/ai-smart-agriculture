from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.services.tts_service import generate_speech


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/tts",
    tags=["Text To Speech"]
)


# =========================================================
# CONSTANTS
# =========================================================

MAX_TTS_TEXT_LENGTH = 3000


# =========================================================
# REQUEST MODEL
# =========================================================

class TTSRequest(BaseModel):

    text: str = Field(
        ...,
        min_length=1,
        max_length=MAX_TTS_TEXT_LENGTH
    )

    language: str = Field(
        ...,
        min_length=1,
        max_length=30
    )


# =========================================================
# TEXT TO SPEECH
# =========================================================

@router.post("/speak")
async def text_to_speech(
    request: TTSRequest
):

    audio_path = None

    try:

        # =====================================================
        # VALIDATE TEXT
        # =====================================================

        text = request.text.strip()

        if not text:

            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty."
            )


        if len(text) > MAX_TTS_TEXT_LENGTH:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Text is too long. "
                    f"Maximum length is "
                    f"{MAX_TTS_TEXT_LENGTH} characters."
                )
            )


        # =====================================================
        # VALIDATE LANGUAGE
        # =====================================================

        language = request.language.strip()

        if not language:

            raise HTTPException(
                status_code=400,
                detail="Language is required."
            )


        # =====================================================
        # GENERATE SPEECH
        # =====================================================

        audio_path = await generate_speech(
            text,
            language
        )


        # =====================================================
        # VALIDATE AUDIO FILE
        # =====================================================

        if not audio_path:

            raise RuntimeError(
                "TTS service returned no audio file."
            )


        # =====================================================
        # RETURN AUDIO
        # =====================================================

        return FileResponse(
            audio_path,
            media_type="audio/mpeg",
            filename="assistant_response.mp3"
        )


    # =========================================================
    # HTTP ERROR
    # =========================================================

    except HTTPException:

        raise


    # =========================================================
    # TTS ERROR
    # =========================================================

    except Exception as error:

        print(
            "TTS generation error:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="TTS generation failed."
        )