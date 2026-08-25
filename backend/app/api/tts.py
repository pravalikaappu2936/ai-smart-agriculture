from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from app.services.tts_service import generate_speech


router = APIRouter(
    prefix="/tts",
    tags=["Text To Speech"]
)


class TTSRequest(BaseModel):
    text: str
    language: str


@router.post("/speak")
async def text_to_speech(request: TTSRequest):

    try:

        if not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty"
            )

        audio_path = await generate_speech(
            request.text,
            request.language
        )

        return FileResponse(
            audio_path,
            media_type="audio/mpeg",
            filename="assistant_response.mp3",
            background=None
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"TTS generation failed: {str(e)}"
        )