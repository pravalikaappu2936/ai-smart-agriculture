from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.market_schema import MarketPriceResponse
from app.services.market_service import (
    MarketAPIError,
    get_market_prices,
)


router = APIRouter(
    prefix="/market",
    tags=["Market Price Analysis"],
)


@router.get(
    "/prices",
    response_model=MarketPriceResponse,
)
async def market_prices(
    commodity: Optional[str] = Query(
        default=None,
        description="Commodity name",
    ),
    state: Optional[str] = Query(
        default=None,
        description="State name",
    ),
    district: Optional[str] = Query(
        default=None,
        description="District name",
    ),
    market: Optional[str] = Query(
        default=None,
        description="Market/Mandi name",
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Number of records",
    ),
):

    try:

        result = await get_market_prices(
            commodity=commodity,
            state=state,
            district=district,
            market=market,
            limit=limit,
        )

        return result

    except MarketAPIError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except Exception as error:

        print(
            "MARKET PRICE API ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Market price analysis failed.",
        ) from error