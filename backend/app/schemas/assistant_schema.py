from typing import Literal

from pydantic import BaseModel, Field


# =========================================================
# SUPPORTED LANGUAGES
# =========================================================

SUPPORTED_LANGUAGES = [
    "English",
    "Kannada",
    "Hindi",
    "Telugu",
    "Tamil",
    "Malayalam",
    "Marathi",
]


# =========================================================
# LANGUAGE TYPE
# =========================================================

LanguageType = Literal[
    "English",
    "Kannada",
    "Hindi",
    "Telugu",
    "Tamil",
    "Malayalam",
    "Marathi",
]


# =========================================================
# AI ASSISTANT REQUEST
# =========================================================

class AssistantRequest(BaseModel):
    """
    Request model for the AI Agriculture Assistant.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's agriculture-related question"
    )

    language: LanguageType = Field(
        default="English",
        description="Preferred response language"
    )


# =========================================================
# AI ASSISTANT RESPONSE
# =========================================================

class AssistantResponse(BaseModel):
    """
    Response model returned by the AI Agriculture Assistant.
    """

    success: bool = Field(
        ...,
        description="Whether the request was processed successfully"
    )

    response: str = Field(
        ...,
        description="AI generated response"
    )

    language: LanguageType = Field(
        ...,
        description="Language used for the AI response"
    )