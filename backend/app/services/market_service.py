import os
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT CONFIGURATION
# ============================================================

# Current file:
# backend/app/services/market_service.py
#
# parents[0] = services
# parents[1] = app
# parents[2] = backend

BASE_DIR = Path(__file__).resolve().parents[2]

# Expected:
# D:\...\AI smart agriculture\backend\.env
ENV_FILE = BASE_DIR / ".env"


# Load .env into the process as well.
# The API key itself is NOT printed.
load_dotenv(
    dotenv_path=ENV_FILE,
    override=True,
)


# ============================================================
# GOVERNMENT DATA.GOV.IN API
# ============================================================

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

OGD_API_URL = (
    f"https://api.data.gov.in/resource/{RESOURCE_ID}"
)


# ============================================================
# CUSTOM EXCEPTION
# ============================================================

class MarketAPIError(Exception):
    """Custom exception for Government Market API errors."""

    pass


# ============================================================
# READ API KEY
# ============================================================

def get_api_key() -> str:
    """
    Read DATA_GOV_API_KEY directly from backend/.env.

    The file is read every time this function is called.
    This avoids problems with Uvicorn reload processes,
    environment inheritance, or dotenv loading.
    """

    print("\n==============================================")
    print("MARKET API KEY CHECK")
    print("==============================================")

    print(
        "SERVICE FILE:",
        Path(__file__).resolve(),
    )

    print(
        "BASE DIR:",
        BASE_DIR,
    )

    print(
        "ENV FILE:",
        ENV_FILE,
    )

    print(
        "ENV FILE EXISTS:",
        ENV_FILE.exists(),
    )

    # --------------------------------------------------------
    # Check .env
    # --------------------------------------------------------

    if not ENV_FILE.exists():

        raise MarketAPIError(
            "backend/.env file was not found."
        )

    # --------------------------------------------------------
    # Read file directly
    # --------------------------------------------------------

    api_key = None

    try:

        with open(
            ENV_FILE,
            "r",
            encoding="utf-8-sig",
        ) as env_file:

            for line in env_file:

                line = line.strip()

                # Ignore empty lines
                if not line:
                    continue

                # Ignore comments
                if line.startswith("#"):
                    continue

                # Look for exact variable
                if line.startswith(
                    "DATA_GOV_API_KEY="
                ):

                    api_key = line.split(
                        "=",
                        1,
                    )[1].strip()

                    break

    except Exception as error:

        print(
            "ENV FILE READ ERROR:",
            repr(error),
        )

        raise MarketAPIError(
            "Unable to read backend/.env file."
        ) from error

    # --------------------------------------------------------
    # Diagnostic information
    # --------------------------------------------------------

    print(
        "DATA_GOV_API_KEY ENTRY FOUND:",
        api_key is not None,
    )

    print(
        "API KEY FOUND:",
        bool(api_key),
    )

    print(
        "API KEY LENGTH:",
        len(api_key or ""),
    )

    print("==============================================\n")

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if api_key is None:

        raise MarketAPIError(
            "DATA_GOV_API_KEY was not found in backend/.env."
        )

    # --------------------------------------------------------
    # Remove optional quotes
    # --------------------------------------------------------

    if (
        len(api_key) >= 2
        and (
            (
                api_key.startswith('"')
                and api_key.endswith('"')
            )
            or (
                api_key.startswith("'")
                and api_key.endswith("'")
            )
        )
    ):

        api_key = api_key[1:-1].strip()

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    if not api_key:

        raise MarketAPIError(
            "DATA_GOV_API_KEY is empty."
        )

    return api_key


# ============================================================
# GET MARKET PRICES
# ============================================================

async def get_market_prices(
    commodity: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    market: Optional[str] = None,
    limit: int = 100,
):
    """
    Fetch daily mandi market prices from
    the Government of India's data.gov.in API.

    Optional filters:
        commodity
        state
        district
        market

    Returns:
        success
        count
        total
        records
    """

    # ========================================================
    # API KEY
    # ========================================================

    api_key = get_api_key()

    # ========================================================
    # LIMIT
    # ========================================================

    limit = min(
        max(limit, 1),
        1000,
    )

    # ========================================================
    # API PARAMETERS
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

    if commodity:

        params["filters[commodity]"] = (
            commodity.strip()
        )

    # ========================================================
    # STATE FILTER
    # ========================================================

    if state:

        params["filters[state.keyword]"] = (
            state.strip()
        )

    # ========================================================
    # DISTRICT FILTER
    # ========================================================

    if district:

        params["filters[district]"] = (
            district.strip()
        )

    # ========================================================
    # MARKET FILTER
    # ========================================================

    if market:

        params["filters[market]"] = (
            market.strip()
        )

    # ========================================================
    # DEBUG INFORMATION
    # ========================================================

    print("\n==============================================")
    print("GOVERNMENT MANDI MARKET API")
    print("==============================================")

    print(
        "Resource:",
        RESOURCE_ID,
    )

    print(
        "URL:",
        OGD_API_URL,
    )

    print(
        "Filters:",
        {
            "commodity": commodity,
            "state": state,
            "district": district,
            "market": market,
        },
    )

    print(
        "Limit:",
        limit,
    )

    print(
        "API key configured:",
        bool(api_key),
    )

    print("==============================================\n")

    # ========================================================
    # API REQUEST
    # ========================================================

    try:

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=20.0,
                read=60.0,
                write=20.0,
                pool=20.0,
            ),
            follow_redirects=True,
            verify=True,
            trust_env=False,
        ) as client:

            response = await client.get(
                OGD_API_URL,
                params=params,
                headers={
                    "Accept": "application/json",
                    "User-Agent": (
                        "AI-Smart-Agriculture/1.0"
                    ),
                },
            )

        # ====================================================
        # RESPONSE INFORMATION
        # ====================================================

        print(
            "Government API status:",
            response.status_code,
        )

        print(
            "Government API content type:",
            response.headers.get(
                "content-type"
            ),
        )

        # ====================================================
        # AUTHENTICATION ERROR
        # ====================================================

        if response.status_code == 401:

            raise MarketAPIError(
                "Government API rejected the API key. "
                "Please verify DATA_GOV_API_KEY."
            )

        # ====================================================
        # FORBIDDEN
        # ====================================================

        if response.status_code == 403:

            raise MarketAPIError(
                "Government API access is forbidden. "
                "Check your API key and API permissions."
            )

        # ====================================================
        # NOT FOUND
        # ====================================================

        if response.status_code == 404:

            raise MarketAPIError(
                "Government market API resource "
                "was not found."
            )

        # ====================================================
        # RATE LIMIT
        # ====================================================

        if response.status_code == 429:

            raise MarketAPIError(
                "Government market API rate limit "
                "exceeded. Please try again later."
            )

        # ====================================================
        # OTHER HTTP ERRORS
        # ====================================================

        response.raise_for_status()

        # ====================================================
        # PARSE JSON
        # ====================================================

        try:

            data = response.json()

        except ValueError as error:

            print(
                "Invalid JSON response:"
            )

            print(
                response.text[:1000]
            )

            raise MarketAPIError(
                "Government market API returned "
                "an invalid response."
            ) from error

        # ====================================================
        # VALIDATE RESPONSE
        # ====================================================

        if not isinstance(data, dict):

            raise MarketAPIError(
                "Government market API returned "
                "an unexpected response."
            )

        # ====================================================
        # RECORDS
        # ====================================================

        records = data.get(
            "records",
            [],
        )

        if not isinstance(records, list):

            records = []

        # ====================================================
        # TOTAL
        # ====================================================

        total = data.get(
            "total",
            len(records),
        )

        try:

            total = int(total)

        except (
            TypeError,
            ValueError,
        ):

            total = len(records)

        # ====================================================
        # DEBUG RESULT
        # ====================================================

        print(
            "Total records available:",
            total,
        )

        print(
            "Records received:",
            len(records),
        )

        # ====================================================
        # SUCCESS RESPONSE
        # ====================================================

        return {
            "success": True,
            "count": len(records),
            "total": total,
            "records": records,
        }

    # ========================================================
    # CONNECTION TIMEOUT
    # ========================================================

    except httpx.ConnectTimeout as error:

        print(
            "MARKET API CONNECT TIMEOUT:",
            repr(error),
        )

        raise MarketAPIError(
            "Connection to the Government market API "
            "timed out."
        ) from error

    # ========================================================
    # READ TIMEOUT
    # ========================================================

    except httpx.ReadTimeout as error:

        print(
            "MARKET API READ TIMEOUT:",
            repr(error),
        )

        raise MarketAPIError(
            "Government market API took too long "
            "to respond."
        ) from error

    # ========================================================
    # CONNECTION ERROR
    # ========================================================

    except httpx.ConnectError as error:

        print(
            "MARKET API CONNECT ERROR:",
            repr(error),
        )

        raise MarketAPIError(
            "Unable to connect to the Government "
            "market API."
        ) from error

    # ========================================================
    # OTHER REQUEST ERROR
    # ========================================================

    except httpx.RequestError as error:

        print(
            "MARKET API REQUEST ERROR:",
            repr(error),
        )

        raise MarketAPIError(
            "Unable to connect to the Government "
            "market API."
        ) from error

    # ========================================================
    # HTTP STATUS ERROR
    # ========================================================

    except httpx.HTTPStatusError as error:

        print(
            "MARKET API HTTP ERROR:",
            error.response.status_code,
        )

        raise MarketAPIError(
            "Government market API returned HTTP "
            f"{error.response.status_code}."
        ) from error