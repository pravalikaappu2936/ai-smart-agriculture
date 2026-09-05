from fastapi import APIRouter, Depends, HTTPException

from app.schemas.assistant_schema import (
    AssistantRequest,
    AssistantResponse
)

from app.services.ai_assistant import (
    get_ai_response,
    normalize_language
)

from app.core.dependencies import get_current_user


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/assistant",
    tags=["AI Assistant"]
)


# =========================================================
# CONSTANTS
# =========================================================

MAX_MESSAGE_LENGTH = 2000


# =========================================================
# AI ASSISTANT CHAT
# =========================================================

@router.post(
    "/chat",
    response_model=AssistantResponse
)
def assistant_chat(
    request: AssistantRequest,
    current_user=Depends(get_current_user)
):
    """
    AI Agriculture Assistant endpoint.

    Request:
        {
            "message": "...",
            "language": "Kannada"
        }

    Response:
        {
            "success": true,
            "response": "...",
            "language": "Kannada"
        }
    """

    try:

        # =====================================================
        # VALIDATE REQUEST
        # =====================================================

        if request is None:

            raise HTTPException(
                status_code=400,
                detail="Request is required."
            )


        # =====================================================
        # VALIDATE MESSAGE
        # =====================================================

        if request.message is None:

            raise HTTPException(
                status_code=400,
                detail="Message is required."
            )


        message = str(
            request.message
        ).strip()


        if not message:

            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty."
            )


        # =====================================================
        # MESSAGE LENGTH PROTECTION
        # =====================================================

        if len(message) > MAX_MESSAGE_LENGTH:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Message is too long. "
                    f"Maximum length is {MAX_MESSAGE_LENGTH} characters."
                )
            )


        # =====================================================
        # NORMALIZE LANGUAGE
        # =====================================================

        try:

            language = normalize_language(
                request.language
            )

        except Exception as error:

            print(
                "Language normalization error:",
                repr(error)
            )

            raise HTTPException(
                status_code=400,
                detail="Unsupported language."
            )


        # =====================================================
        # LOG REQUEST
        # =====================================================

        print(
            "========================================"
        )

        print(
            "AI ASSISTANT REQUEST"
        )

        print(
            "User:",
            getattr(
                current_user,
                "username",
                "unknown"
            )
        )

        print(
            "Message length:",
            len(message)
        )

        print(
            "Language:",
            language
        )

        print(
            "========================================"
        )


        # =====================================================
        # GET AI RESPONSE
        # =====================================================

        response = get_ai_response(
            message=message,
            language=language
        )


        # =====================================================
        # VALIDATE AI RESPONSE
        # =====================================================

        if response is None:

            raise RuntimeError(
                "AI assistant returned no response."
            )


        response = str(
            response
        ).strip()


        if not response:

            raise RuntimeError(
                "AI assistant returned an empty response."
            )


        # =====================================================
        # LOG RESPONSE INFORMATION
        # =====================================================

        print(
            "========================================"
        )

        print(
            "AI ASSISTANT RESPONSE"
        )

        print(
            "Language:",
            language
        )

        print(
            "Response length:",
            len(response)
        )

        print(
            "========================================"
        )


        # =====================================================
        # RETURN RESPONSE
        # =====================================================

        return AssistantResponse(
            success=True,
            response=response,
            language=language
        )


    # =========================================================
    # HTTP ERROR
    # =========================================================

    except HTTPException:

        raise


    # =========================================================
    # RUNTIME ERROR
    # =========================================================

    except RuntimeError as error:

        print(
            "AI Assistant Runtime Error:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


    # =========================================================
    # VALUE ERROR
    # =========================================================

    except ValueError as error:

        print(
            "AI Assistant Value Error:",
            repr(error)
        )

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


    # =========================================================
    # UNEXPECTED ERROR
    # =========================================================

    except Exception as error:

        print(
            "AI Assistant Unexpected Error:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to process AI assistant request."
        )