from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.schemas.assistant_schema import (
    AssistantRequest,
    AssistantResponse
)

from app.services.ai_assistant import (
    get_ai_response,
    normalize_language
)

from app.core.dependencies import (
    get_current_user
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/assistant",
    tags=["AI Assistant"]
)


# =========================================================
# AI CHAT
# =========================================================

@router.post(
    "/chat",
    response_model=AssistantResponse
)
def assistant_chat(
    request: AssistantRequest,
    current_user=Depends(get_current_user)
):

    try:

        # -------------------------------------------------
        # VALIDATE MESSAGE
        # -------------------------------------------------

        message = request.message.strip()

        if not message:

            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty."
            )

        # -------------------------------------------------
        # NORMALIZE LANGUAGE
        # -------------------------------------------------

        language = normalize_language(
            request.language
        )

        # -------------------------------------------------
        # GET AI RESPONSE
        # -------------------------------------------------

        response = get_ai_response(

            message=message,

            language=language

        )

        # -------------------------------------------------
        # RETURN RESPONSE
        # -------------------------------------------------

        return AssistantResponse(

            success=True,

            response=response,

            language=language

        )

    except HTTPException:

        raise

    except RuntimeError as error:

        raise HTTPException(

            status_code=500,

            detail=str(error)

        )

    except ValueError as error:

        raise HTTPException(

            status_code=400,

            detail=str(error)

        )

    except Exception as error:

        print(
            "AI Assistant Error:",
            repr(error)
        )

        raise HTTPException(

            status_code=500,

            detail="Unable to process AI assistant request."

        )