import re
import time
from typing import Optional, Tuple

import requests


# =========================================================
# OPEN-METEO URLS
# =========================================================

GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


# =========================================================
# CACHE SETTINGS
# =========================================================

# Weather does not need to be requested every few seconds.
# 10 minutes is enough for this application.
WEATHER_CACHE_TTL = 600

# Location results can also be cached.
LOCATION_CACHE_TTL = 3600

# Maximum time to wait when Open-Meteo returns 429.
MAX_RETRY_WAIT = 20


# =========================================================
# IN-MEMORY CACHE
# =========================================================

_weather_cache = {}

_location_cache = {}


# =========================================================
# HTTP SESSION
# =========================================================

session = requests.Session()

session.headers.update(
    {
        "User-Agent": "AI-Smart-Agriculture/1.0"
    }
)


# =========================================================
# NORMALIZE LOCATION TEXT
# =========================================================

def normalize_location_text(value: str) -> str:
    """
    Normalize location text.

    Examples:

        Karnataka
        karnataka
        KARNATAKA
        KaRnAtAkA

    All become the same normalized value.
    """

    if value is None:
        return ""

    return " ".join(
        str(value)
        .strip()
        .split()
    ).casefold()


# =========================================================
# PARSE COORDINATES
# =========================================================

def parse_coordinates(
    location: str
) -> Optional[Tuple[float, float]]:
    """
    Detect coordinate strings such as:

        14.2380, 76.3933
        14.2380,76.3933
        -14.2380, 76.3933

    Returns:

        (latitude, longitude)

    or:

        None
    """

    if not location:
        return None

    location = str(location).strip()

    # -----------------------------------------------------
    # CORRECT COORDINATE REGEX
    # -----------------------------------------------------

    pattern = (
        r"^\s*"
        r"(-?\d+(?:\.\d+)?)"
        r"\s*,\s*"
        r"(-?\d+(?:\.\d+)?)"
        r"\s*$"
    )

    match = re.match(
        pattern,
        location
    )

    if not match:
        return None

    try:

        latitude = float(
            match.group(1)
        )

        longitude = float(
            match.group(2)
        )

    except ValueError:

        return None

    # -----------------------------------------------------
    # VALIDATE LATITUDE
    # -----------------------------------------------------

    if latitude < -90 or latitude > 90:
        return None

    # -----------------------------------------------------
    # VALIDATE LONGITUDE
    # -----------------------------------------------------

    if longitude < -180 or longitude > 180:
        return None

    return latitude, longitude


# =========================================================
# CACHE HELPER
# =========================================================

def _get_cache(
    cache: dict,
    key,
    ttl: int
):

    item = cache.get(key)

    if not item:
        return None

    timestamp, value = item

    if time.time() - timestamp > ttl:

        cache.pop(
            key,
            None
        )

        return None

    return value


def _set_cache(
    cache: dict,
    key,
    value
):

    cache[key] = (
        time.time(),
        value
    )


# =========================================================
# WEATHER CACHE KEY
# =========================================================

def _weather_cache_key(
    latitude: float,
    longitude: float
):

    return (
        round(float(latitude), 3),
        round(float(longitude), 3)
    )


# =========================================================
# REQUEST OPEN-METEO WITH 429 HANDLING
# =========================================================

def _request_open_meteo(
    url: str,
    params: dict,
    timeout: int = 15
):

    try:

        response = session.get(
            url,
            params=params,
            timeout=timeout
        )

        # -------------------------------------------------
        # RATE LIMIT
        # -------------------------------------------------

        if response.status_code == 429:

            retry_after = response.headers.get(
                "Retry-After"
            )

            try:

                wait_seconds = int(
                    retry_after
                )

            except (
                TypeError,
                ValueError
            ):

                wait_seconds = 5

            wait_seconds = min(
                wait_seconds,
                MAX_RETRY_WAIT
            )

            raise requests.HTTPError(
                f"429 Too Many Requests. "
                f"Retry after approximately "
                f"{wait_seconds} seconds."
            )

        response.raise_for_status()

        return response.json()

    except requests.Timeout:

        raise Exception(
            "Weather service timed out. "
            "Please try again."
        )

    except requests.HTTPError as exc:

        raise Exception(
            f"Unable to connect to weather service: {exc}"
        )

    except requests.RequestException as exc:

        raise Exception(
            f"Unable to connect to weather service: {exc}"
        )


# =========================================================
# SEARCH LOCATIONS
# =========================================================

def search_locations(
    village: str,
    district: str = "",
    state: str = "",
):
    """
    Search locations using village, district and state.

    Search is case-insensitive.
    Coordinate input is supported.
    """

    # =====================================================
    # NORMALIZE INPUT
    # =====================================================

    village = normalize_location_text(
        village
    )

    district = normalize_location_text(
        district
    )

    state = normalize_location_text(
        state
    )

    # =====================================================
    # VILLAGE REQUIRED
    # =====================================================

    if not village:
        return []

    # =====================================================
    # CHECK COORDINATES
    # =====================================================

    coordinates = parse_coordinates(
        village
    )

    if coordinates:

        latitude, longitude = coordinates

        return [
            {
                "name": "Selected Location",
                "latitude": latitude,
                "longitude": longitude,
                "country": "India",
                "state": "",
                "district": "",
                "timezone": "",
                "display_name":
                    f"{latitude}, {longitude}",
            }
        ]

    # =====================================================
    # CACHE KEY
    # =====================================================

    cache_key = (
        village,
        district,
        state
    )

    cached = _get_cache(
        _location_cache,
        cache_key,
        LOCATION_CACHE_TTL
    )

    if cached is not None:

        return cached

    # =====================================================
    # SEARCH QUERIES
    # =====================================================

    search_queries = []

    if district and state:

        search_queries.append(
            f"{village}, {district}, {state}, India"
        )

    if state:

        search_queries.append(
            f"{village}, {state}, India"
        )

    search_queries.append(
        f"{village}, India"
    )

    all_results = []

    # =====================================================
    # CALL GEOCODING API
    # =====================================================

    try:

        for query in search_queries:

            data = _request_open_meteo(
                GEOCODING_URL,
                {
                    "name": query,
                    "count": 10,
                    "language": "en",
                    "format": "json",
                },
                timeout=8
            )

            results = data.get(
                "results",
                []
            )

            all_results.extend(
                results
            )

            # -------------------------------------------------
            # CHECK INDIAN RESULTS
            # -------------------------------------------------

            indian_results = [
                item
                for item in all_results
                if item.get(
                    "country_code"
                ) == "IN"
            ]

            if len(indian_results) >= 5:

                break

    except Exception:

        raise

    # =====================================================
    # KEEP INDIAN RESULTS
    # =====================================================

    india_results = [
        item
        for item in all_results
        if item.get(
            "country_code"
        ) == "IN"
    ]

    if not india_results:

        india_results = all_results

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    unique_results = []

    seen = set()

    for item in india_results:

        latitude = item.get(
            "latitude"
        )

        longitude = item.get(
            "longitude"
        )

        if (
            latitude is None
            or longitude is None
        ):
            continue

        try:

            latitude = float(
                latitude
            )

            longitude = float(
                longitude
            )

        except (
            TypeError,
            ValueError
        ):

            continue

        key = (
            round(latitude, 6),
            round(longitude, 6)
        )

        if key in seen:
            continue

        seen.add(key)

        # -------------------------------------------------
        # LOCATION INFORMATION
        # -------------------------------------------------

        name = item.get(
            "name",
            village
        )

        country = item.get(
            "country",
            "India"
        )

        result_state = item.get(
            "admin1",
            ""
        )

        result_district = item.get(
            "admin2",
            ""
        )

        # -------------------------------------------------
        # DISPLAY NAME
        # -------------------------------------------------

        display_parts = [
            name,
            result_district,
            result_state,
            country
        ]

        display_name = ", ".join(
            str(part)
            for part in display_parts
            if part
        )

        unique_results.append(
            {
                "name": name,
                "latitude": latitude,
                "longitude": longitude,
                "country": country,
                "state": result_state,
                "district": result_district,
                "timezone":
                    item.get(
                        "timezone",
                        ""
                    ),
                "display_name":
                    display_name,
            }
        )

    # =====================================================
    # RANK RESULTS
    # =====================================================

    def result_score(item):

        score = 0

        item_state = normalize_location_text(
            item.get(
                "state",
                ""
            ) or ""
        )

        item_district = normalize_location_text(
            item.get(
                "district",
                ""
            ) or ""
        )

        requested_state = normalize_location_text(
            state
        )

        requested_district = normalize_location_text(
            district
        )

        if requested_state:

            if requested_state in item_state:

                score += 20

        if requested_district:

            if requested_district in item_district:

                score += 30

        return score

    # =====================================================
    # SORT
    # =====================================================

    unique_results.sort(
        key=result_score,
        reverse=True
    )

    # =====================================================
    # LIMIT RESULTS
    # =====================================================

    final_results = unique_results[:8]

    # =====================================================
    # CACHE
    # =====================================================

    _set_cache(
        _location_cache,
        cache_key,
        final_results
    )

    return final_results


# =========================================================
# LOCATION COORDINATES
# =========================================================

def get_location_coordinates(
    location: str
):
    """
    Convert a location name into coordinates.
    """

    if (
        not location
        or not str(location).strip()
    ):

        raise ValueError(
            "Location cannot be empty."
        )

    location = str(
        location
    ).strip()

    # =====================================================
    # CHECK COORDINATES FIRST
    # =====================================================

    coordinates = parse_coordinates(
        location
    )

    if coordinates:

        latitude, longitude = coordinates

        return {
            "name":
                "Selected Location",

            "latitude":
                latitude,

            "longitude":
                longitude,

            "country":
                "India",

            "state":
                "",

            "district":
                "",

            "timezone":
                "",

            "display_name":
                f"{latitude}, {longitude}",
        }

    # =====================================================
    # NORMALIZE
    # =====================================================

    normalized_location = normalize_location_text(
        location
    )

    # =====================================================
    # CACHE
    # =====================================================

    cache_key = (
        "coordinates",
        normalized_location
    )

    cached = _get_cache(
        _location_cache,
        cache_key,
        LOCATION_CACHE_TTL
    )

    if cached is not None:

        return cached

    # =====================================================
    # CALL GEOCODING API
    # =====================================================

    try:

        data = _request_open_meteo(
            GEOCODING_URL,
            {
                "name":
                    normalized_location,

                "count":
                    10,

                "language":
                    "en",

                "format":
                    "json",
            },
            timeout=10
        )

    except Exception as exc:

        raise Exception(
            str(exc)
        )

    # =====================================================
    # RESULTS
    # =====================================================

    results = data.get(
        "results",
        []
    )

    if not results:

        raise ValueError(
            f"Location '{location}' could not be found."
        )

    # =====================================================
    # PREFER INDIA
    # =====================================================

    india_results = [
        item
        for item in results
        if item.get(
            "country_code"
        ) == "IN"
    ]

    result = (
        india_results[0]
        if india_results
        else results[0]
    )

    # =====================================================
    # COORDINATES
    # =====================================================

    latitude = result.get(
        "latitude"
    )

    longitude = result.get(
        "longitude"
    )

    if (
        latitude is None
        or longitude is None
    ):

        raise ValueError(
            "Coordinates were not available "
            "for this location."
        )

    try:

        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )

    except (
        TypeError,
        ValueError
    ):

        raise ValueError(
            "Invalid coordinates returned "
            "by location service."
        )

    # =====================================================
    # VALIDATE
    # =====================================================

    if latitude < -90 or latitude > 90:

        raise ValueError(
            "Invalid latitude returned "
            "by location service."
        )

    if longitude < -180 or longitude > 180:

        raise ValueError(
            "Invalid longitude returned "
            "by location service."
        )

    # =====================================================
    # LOCATION DETAILS
    # =====================================================

    name = result.get(
        "name",
        location
    )

    country = result.get(
        "country",
        ""
    )

    state = result.get(
        "admin1",
        ""
    )

    district = result.get(
        "admin2",
        ""
    )

    # =====================================================
    # DISPLAY NAME
    # =====================================================

    display_parts = [
        name,
        district,
        state,
        country
    ]

    display_name = ", ".join(
        str(part)
        for part in display_parts
        if part
    )

    # =====================================================
    # RESULT
    # =====================================================

    location_data = {

        "name":
            name,

        "latitude":
            latitude,

        "longitude":
            longitude,

        "country":
            country,

        "state":
            state,

        "district":
            district,

        "timezone":
            result.get(
                "timezone",
                ""
            ),

        "display_name":
            display_name,
    }

    # =====================================================
    # CACHE
    # =====================================================

    _set_cache(
        _location_cache,
        cache_key,
        location_data
    )

    return location_data


# =========================================================
# CURRENT WEATHER
# =========================================================

def get_current_weather(
    latitude: float,
    longitude: float
):
    """
    Get current weather and 7-day forecast.

    Weather data is cached for 10 minutes.
    """

    # =====================================================
    # CONVERT COORDINATES
    # =====================================================

    try:

        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )

    except (
        TypeError,
        ValueError
    ):

        raise ValueError(
            "Invalid latitude or longitude."
        )

    # =====================================================
    # VALIDATE
    # =====================================================

    if latitude < -90 or latitude > 90:

        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    if longitude < -180 or longitude > 180:

        raise ValueError(
            "Longitude must be between -180 and 180."
        )

    # =====================================================
    # CACHE KEY
    # =====================================================

    cache_key = _weather_cache_key(
        latitude,
        longitude
    )

    # =====================================================
    # CHECK CACHE
    # =====================================================

    cached = _get_cache(
        _weather_cache,
        cache_key,
        WEATHER_CACHE_TTL
    )

    if cached is not None:

        print(
            "Weather cache HIT:",
            cache_key
        )

        return cached

    print(
        "Weather cache MISS:",
        cache_key
    )

    # =====================================================
    # WEATHER PARAMETERS
    # =====================================================

    params = {

        "latitude":
            latitude,

        "longitude":
            longitude,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "rain,"
            "weather_code,"
            "wind_speed_10m"
        ),

        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max,"
            "weather_code,"
            "wind_speed_10m_max"
        ),

        "timezone":
            "auto",

        "forecast_days":
            7,
    }

    # =====================================================
    # REQUEST WEATHER
    # =====================================================

    try:

        data = _request_open_meteo(
            WEATHER_URL,
            params,
            timeout=15
        )

    except Exception as exc:

        # -------------------------------------------------
        # IMPORTANT:
        # If Open-Meteo is rate limited but old cached
        # data exists, return the old data instead of
        # breaking irrigation/weather.
        # -------------------------------------------------

        old_cached = _weather_cache.get(
            cache_key
        )

        if old_cached:

            print(
                "Open-Meteo unavailable. "
                "Returning stale weather cache."
            )

            return old_cached[1]

        raise Exception(
            str(exc)
        )

    # =====================================================
    # NORMALIZED RESPONSE
    # =====================================================

    weather_data = {

        "latitude":
            data.get(
                "latitude"
            ),

        "longitude":
            data.get(
                "longitude"
            ),

        "timezone":
            data.get(
                "timezone"
            ),

        "current":
            data.get(
                "current",
                {}
            ),

        "forecast":
            data.get(
                "daily",
                {}
            ),
    }

    # =====================================================
    # SAVE CACHE
    # =====================================================

    _set_cache(
        _weather_cache,
        cache_key,
        weather_data
    )

    return weather_data


# =========================================================
# WEATHER BY LOCATION
# =========================================================

def get_weather_for_location(
    location: str
):
    """
    Get weather using a location name.
    """

    location_data = (
        get_location_coordinates(
            location
        )
    )

    weather_data = (
        get_current_weather(
            location_data[
                "latitude"
            ],
            location_data[
                "longitude"
            ]
        )
    )

    weather_data[
        "location"
    ] = location_data

    return weather_data


# =========================================================
# WEATHER BY COORDINATES
# =========================================================

def get_weather_by_coordinates(
    latitude: float,
    longitude: float
):
    """
    Get weather directly using coordinates.
    """

    # =====================================================
    # CONVERT
    # =====================================================

    try:

        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )

    except (
        TypeError,
        ValueError
    ):

        raise ValueError(
            "Invalid latitude or longitude."
        )

    # =====================================================
    # VALIDATE
    # =====================================================

    if latitude < -90 or latitude > 90:

        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    if longitude < -180 or longitude > 180:

        raise ValueError(
            "Longitude must be between -180 and 180."
        )

    # =====================================================
    # WEATHER
    # =====================================================

    weather_data = (
        get_current_weather(
            latitude,
            longitude
        )
    )

    # =====================================================
    # ATTACH LOCATION
    # =====================================================

    weather_data[
        "location"
    ] = {

        "name":
            "Selected Location",

        "latitude":
            latitude,

        "longitude":
            longitude,

        "country":
            "India",
    }

    return weather_data