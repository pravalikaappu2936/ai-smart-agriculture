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
    "Marathi"
]


# =========================================================
# AI ASSISTANT REQUEST
# =========================================================

class AssistantRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's agriculture-related question"
    )

    language: str = Field(
        default="English",
        description="Preferred response language"
    )


# =========================================================
# AI ASSISTANT RESPONSE
# =========================================================

class AssistantResponse(BaseModel):

    success: bool

    response: str

    language: str