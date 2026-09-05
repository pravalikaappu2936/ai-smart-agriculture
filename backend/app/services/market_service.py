import os
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv


# ============================================================
# PATHS
# ============================================================

# backend/
# └── app/
#     └── services/
#         └── market_service.py
#
# parents[0] = services
# parents[1] = app
# parents[2] = backend

BASE_DIR = Path(__file__).resolve().parents[2]

ENV_FILE = BASE_DIR / ".env"


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

# Local development:
#     backend/.env
#
# Render:
#     DATA_GOV_API_KEY must be configured in
#     Render Environment Variables.
#
# .env is optional.

if ENV_FILE.exists():
    load_dotenv(
        dotenv_path=ENV_FILE,
        override=False,
    )


# ============================================================
# GOVERNMENT MARKET API
# ============================================================

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

OGD_API_URL = (
    f"https://api.data.gov.in/resource/{RESOURCE_ID}"
)


# ============================================================
# CUSTOM EXCEPTION
# ============================================================

class MarketAPIError(Exception):
    """Raised when the government market API cannot be used."""
    pass


# ============================================================
# API KEY
# ============================================================

def get_api_key() -> str:
    """
    Get the Data.gov.in API key.

    Local:
        Reads DATA_GOV_API_KEY from backend/.env.

    Render:
        Reads DATA_GOV_API_KEY from Render environment
        variables.

    The actual API key is never printed.
    """

    # Load .env again in case the environment variable
    # was not loaded during module import.
    if ENV_FILE.exists():
        load_dotenv(
            dotenv_path=ENV_FILE,
            override=False,
        )

    # IMPORTANT:
    # Use the VARIABLE NAME here, not the actual API key.
    api_key = os.getenv("DATA_GOV_API_KEY")

    if not api_key:
        raise MarketAPIError(
            "DATA_GOV_API_KEY environment variable "
            "is not configured."
        )

    # Remove accidental spaces or surrounding quotes.
    api_key = (
        api_key
        .strip()
        .strip('"')
        .strip("'")
    )

    if not api_key:
        raise MarketAPIError(
            "DATA_GOV_API_KEY environment variable "
            "is empty."
        )

    return api_key


# ============================================================
# NORMALIZE MARKET RECORD
# ============================================================

def normalize_market_record(record: dict) -> dict:
    """
    Convert the Data.gov.in record into the structure
    expected by the frontend.
    """

    return {
        "state": record.get("state"),
        "district": record.get("district"),
        "market": record.get("market"),
        "commodity": record.get("commodity"),
        "variety": record.get("variety"),
        "grade": record.get("grade"),
        "arrival_date": record.get("arrival_date"),
        "min_price": record.get("min_price"),
        "max_price": record.get("max_price"),
        "modal_price": record.get("modal_price"),
    }


# ============================================================
# GET MARKET PRICES
# ============================================================

async def get_market_prices(
    commodity: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    market: Optional[str] = None,
    limit: int = 100,
) -> dict:
    """
    Fetch latest mandi market prices from the official
    Data.gov.in agriculture market-price API.
    """

    # ========================================================
    # VALIDATE LIMIT
    # ========================================================

    if limit < 1 or limit > 1000:
        raise MarketAPIError(
            "Market price limit must be between 1 and 1000."
        )


    # ========================================================
    # GET API KEY
    # ========================================================

    api_key = get_api_key()


    # ========================================================
    # BUILD REQUEST PARAMETERS
    # ========================================================

    params = {
        "api-key": api_key,
        "format": "json",
        "limit": limit,
        "offset": 0,
    }


    # ========================================================
    # COMMODITY FILTER
    # ========================================================

    if commodity and commodity.strip():
        params["filters[commodity]"] = commodity.strip()


    # ========================================================
    # STATE FILTER
    # ========================================================

    if state and state.strip():
        params["filters[state.keyword]"] = state.strip()


    # ========================================================
    # DISTRICT FILTER
    # ========================================================

    if district and district.strip():
        params["filters[district]"] = district.strip()


    # ========================================================
    # MARKET FILTER
    # ========================================================

    if market and market.strip():
        params["filters[market]"] = market.strip()


    # ========================================================
    # SAFE DEBUG INFORMATION
    # ========================================================

    # Never print the API key.

    debug_params = {
        key: value
        for key, value in params.items()
        if key != "api-key"
    }

    print(
        "MARKET API REQUEST:",
        debug_params,
    )


    # ========================================================
    # HTTP TIMEOUT
    # ========================================================

    timeout = httpx.Timeout(
        connect=20.0,
        read=60.0,
        write=20.0,
        pool=20.0,
    )


    # ========================================================
    # API REQUEST
    # ========================================================

    try:

        async with httpx.AsyncClient(
            follow_redirects=True,
            verify=True,
            trust_env=False,
            timeout=timeout,
        ) as client:

            response = await client.get(
                OGD_API_URL,
                params=params,
            )


        # ====================================================
        # HTTP STATUS HANDLING
        # ====================================================

        if response.status_code == 401:
            raise MarketAPIError(
                "Data.gov.in API authentication failed. "
                "Check DATA_GOV_API_KEY."
            )


        if response.status_code == 403:
            raise MarketAPIError(
                "Data.gov.in API access was forbidden. "
                "Check the API key and API permissions."
            )


        if response.status_code == 404:
            raise MarketAPIError(
                "Data.gov.in market price resource "
                "was not found."
            )


        if response.status_code == 429:
            raise MarketAPIError(
                "Data.gov.in API rate limit exceeded. "
                "Please try again later."
            )


        if response.status_code >= 400:
            raise MarketAPIError(
                "Data.gov.in API returned HTTP "
                f"{response.status_code}."
            )


        # ====================================================
        # PARSE JSON
        # ====================================================

        try:

            data = response.json()

        except ValueError as error:

            print(
                "MARKET API INVALID JSON:",
                response.text[:500],
            )

            raise MarketAPIError(
                "Data.gov.in returned an invalid response."
            ) from error


        # ====================================================
        # EXTRACT RECORDS
        # ====================================================

        records = data.get(
            "records",
            [],
        )


        if not isinstance(records, list):
            raise MarketAPIError(
                "Invalid market price data received "
                "from Data.gov.in."
            )


        # ====================================================
        # NORMALIZE RECORDS
        # ====================================================

        normalized_records = [
            normalize_market_record(record)
            for record in records
            if isinstance(record, dict)
        ]


        # ====================================================
        # TOTAL RECORD COUNT
        # ====================================================

        total = data.get(
            "total",
            len(normalized_records),
        )


        try:

            total = int(total)

        except (TypeError, ValueError):

            total = len(normalized_records)


        # ====================================================
        # FINAL RESPONSE
        # ====================================================

        result = {
            "success": True,
            "count": len(normalized_records),
            "total": total,
            "records": normalized_records,
        }


        print(
            "MARKET API RESPONSE:",
            {
                "count": result["count"],
                "total": result["total"],
            },
        )


        return result


    # ========================================================
    # TIMEOUT ERROR
    # ========================================================

    except httpx.TimeoutException as error:

        print(
            "MARKET API TIMEOUT:",
            str(error),
        )

        raise MarketAPIError(
            "Data.gov.in market API request timed out."
        ) from error


    # ========================================================
    # CONNECTION ERROR
    # ========================================================

    except httpx.RequestError as error:

        print(
            "MARKET API REQUEST ERROR:",
            str(error),
        )

        raise MarketAPIError(
            "Unable to connect to Data.gov.in market API."
        ) from error