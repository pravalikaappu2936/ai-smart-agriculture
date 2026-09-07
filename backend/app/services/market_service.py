import json
from pathlib import Path
from typing import Optional

CACHE_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "market_cache.json"
)


class MarketAPIError(Exception):
    pass


def _load_cache() -> dict:
    if not CACHE_PATH.exists():
        raise MarketAPIError("Market price cache is not available.")

    try:
        with CACHE_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as error:
        raise MarketAPIError(
            f"Unable to read market price cache: {error}"
        ) from error

    if not isinstance(data, dict):
        raise MarketAPIError("Invalid market price cache format.")

    return data


def _matches(value, requested: Optional[str]) -> bool:
    if not requested:
        return True

    if value is None:
        return False

    return (
        str(value).strip().casefold()
        == requested.strip().casefold()
    )


async def get_market_prices(
    commodity: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    market: Optional[str] = None,
    limit: int = 100,
):
    cache = _load_cache()

    records = cache.get("records", [])

    if not isinstance(records, list):
        raise MarketAPIError("Invalid records in market price cache.")

    # -----------------------------------------
    # STATE FILTER
    # -----------------------------------------
    if state:
        records = [
            record
            for record in records
            if _matches(record.get("state"), state)
        ]

    # -----------------------------------------
    # DISTRICT FILTER
    # -----------------------------------------
    if district:
        records = [
            record
            for record in records
            if _matches(record.get("district"), district)
        ]

    # -----------------------------------------
    # COMMODITY FILTER
    # -----------------------------------------
    if commodity:
        records = [
            record
            for record in records
            if _matches(record.get("commodity"), commodity)
        ]

    # -----------------------------------------
    # MARKET/APMC FILTER
    # -----------------------------------------
    if market:
        records = [
            record
            for record in records
            if _matches(record.get("market"), market)
        ]

    # Remove malformed records
    records = [
        record
        for record in records
        if isinstance(record, dict)
    ]

    return {
        "success": True,
        "count": len(records[:limit]),
        "total": len(records),
        "records": records[:limit],
    }