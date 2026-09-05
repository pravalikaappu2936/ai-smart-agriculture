from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MarketPriceRecord(BaseModel):
    """
    Single mandi market-price record.
    """

    state: Optional[str] = None

    district: Optional[str] = None

    market: Optional[str] = None

    commodity: Optional[str] = None

    variety: Optional[str] = None

    grade: Optional[str] = None

    arrival_date: Optional[str] = None

    min_price: Optional[float] = None

    max_price: Optional[float] = None

    modal_price: Optional[float] = None


class MarketPriceResponse(BaseModel):
    """
    Response from the market price endpoint.
    """

    success: bool = True

    count: int = Field(
        default=0,
        ge=0,
    )

    total: int = Field(
        default=0,
        ge=0,
    )

    records: List[Dict[str, Any]] = Field(
        default_factory=list,
    )