import re
import time
import threading
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

# Fresh weather data is used for 10 minutes.
WEATHER_CACHE_TTL = 600

# Location/geocoding data is cached for 1 hour.
LOCATION_CACHE_TTL = 3600

# Maximum number of retries for temporary 429 responses.
MAX_RETRIES = 2

# Maximum time to wait for a Retry-After response.
MAX_RETRY_WAIT = 20


# =========================================================
# IN-MEMORY CACHE
# =========================================================

_weather_cache = {}
_location_cache = {}


# =========================================================
# CACHE LOCKS
# =========================================================

# Protect cache access when multiple Render requests
# arrive at the same time.
_weather_cache_lock = threading.Lock()
_location_cache_lock = threading.Lock()


# =========================================================
# WEATHER REQUEST LOCKS
# =========================================================

# Prevent multiple simultaneous requests for exactly the
# same coordinates from hitting Open-Meteo.
_weather_request_locks = {}
_weather_request_locks_lock = threading.Lock()


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
    location: str,
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

    pattern = (
        r"^\s*"
        r"(-?\d+(?:\.\d+)?)"
        r"\s*,\s*"
        r"(-?\d+(?:\.\d+)?)"
        r"\s*$"
    )

    match = re.match(
        pattern,
        location,
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
# CACHE GET
# =========================================================

def _get_cache(
    cache: dict,
    key,
    ttl: int,
    lock: Optional[threading.Lock] = None,
):
    """
    Get fresh cached value.

    Returns None when:
        - key does not exist
        - cache entry expired
    """

    if lock is not None:
        with lock:
            item = cache.get(key)
    else:
        item = cache.get(key)

    if not item:
        return None

    timestamp, value = item

    if time.time() - timestamp > ttl:

        if lock is not None:
            with lock:
                cache.pop(
                    key,
                    None,
                )
        else:
            cache.pop(
                key,
                None,
            )

        return None

    return value


# =========================================================
# STALE CACHE GET
# =========================================================

def _get_stale_cache(
    cache: dict,
    key,
    lock: Optional[threading.Lock] = None,
):
    """
    Return cached value even if it is older than the
    normal TTL.

    Used as a fallback when Open-Meteo is temporarily
    unavailable or rate-limited.
    """

    if lock is not None:
        with lock:
            item = cache.get(key)
    else:
        item = cache.get(key)

    if not item:
        return None

    return item[1]


# =========================================================
# CACHE SET
# =========================================================

def _set_cache(
    cache: dict,
    key,
    value,
    lock: Optional[threading.Lock] = None,
):
    """
    Store value in cache.
    """

    item = (
        time.time(),
        value,
    )

    if lock is not None:
        with lock:
            cache[key] = item
    else:
        cache[key] = item


# =========================================================
# WEATHER CACHE KEY
# =========================================================

def _weather_cache_key(
    latitude: float,
    longitude: float,
):
    """
    Round coordinates so tiny GPS differences do not
    create unnecessary Open-Meteo requests.
    """

    return (
        round(float(latitude), 3),
        round(float(longitude), 3),
    )


# =========================================================
# WEATHER REQUEST LOCK
# =========================================================

def _get_weather_request_lock(key):
    """
    Get a lock for a specific coordinate pair.

    This prevents requests like:

        Weather request 1
        Weather request 2
        Irrigation request
        Dashboard request

    from all hitting Open-Meteo simultaneously for
    the same location.
    """

    with _weather_request_locks_lock:

        lock = _weather_request_locks.get(key)

        if lock is None:

            lock = threading.Lock()

            _weather_request_locks[key] = lock

        return lock


# =========================================================
# REQUEST OPEN-METEO
# =========================================================

def _request_open_meteo(
    url: str,
    params: dict,
    timeout: int = 15,
):
    """
    Request Open-Meteo with proper timeout and
    429 retry handling.

    Important:
    A 429 response is actually retried instead of
    immediately raising an error.
    """

    last_error = None

    for attempt in range(
        MAX_RETRIES + 1
    ):

        try:

            response = session.get(
                url,
                params=params,
                timeout=timeout,
            )

            # =================================================
            # RATE LIMIT
            # =================================================

            if response.status_code == 429:

                retry_after = response.headers.get(
                    "Retry-After"
                )

                try:

                    wait_seconds = float(
                        retry_after
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    # Exponential fallback:
                    # attempt 0 -> 5 seconds
                    # attempt 1 -> 10 seconds
                    wait_seconds = (
                        5 * (2 ** attempt)
                    )

                wait_seconds = min(
                    wait_seconds,
                    MAX_RETRY_WAIT,
                )

                last_error = (
                    "429 Too Many Requests. "
                    f"Retry after approximately "
                    f"{int(wait_seconds)} seconds."
                )

                print(
                    "Open-Meteo rate limit "
                    f"(attempt {attempt + 1}/"
                    f"{MAX_RETRIES + 1}). "
                    f"Waiting {wait_seconds:.0f}s."
                )

                # Don't sleep after the final attempt.
                if attempt < MAX_RETRIES:

                    time.sleep(
                        wait_seconds
                    )

                    continue

                raise Exception(
                    last_error
                )

            # =================================================
            # OTHER HTTP ERRORS
            # =================================================

            response.raise_for_status()

            return response.json()

        except requests.Timeout as exc:

            last_error = (
                "Weather service timed out. "
                "Please try again."
            )

            print(
                "Open-Meteo timeout:",
                exc,
            )

            if attempt < MAX_RETRIES:

                time.sleep(
                    2 ** attempt
                )

                continue

            raise Exception(
                last_error
            ) from exc

        except requests.HTTPError as exc:

            last_error = (
                "Unable to connect to weather "
                f"service: {exc}"
            )

            print(
                "Open-Meteo HTTP error:",
                exc,
            )

            # Don't repeatedly retry ordinary HTTP errors.
            raise Exception(
                last_error
            ) from exc

        except requests.RequestException as exc:

            last_error = (
                "Unable to connect to weather "
                f"service: {exc}"
            )

            print(
                "Open-Meteo request error:",
                exc,
            )

            if attempt < MAX_RETRIES:

                time.sleep(
                    2 ** attempt
                )

                continue

            raise Exception(
                last_error
            ) from exc

        except ValueError as exc:

            raise Exception(
                "Invalid response received "
                "from weather service."
            ) from exc

        except Exception:
            raise

    raise Exception(
        last_error
        or "Unable to connect to weather service."
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
                "display_name": (
                    f"{latitude}, {longitude}"
                ),
            }
        ]

    # =====================================================
    # CACHE KEY
    # =====================================================

    cache_key = (
        village,
        district,
        state,
    )

    cached = _get_cache(
        _location_cache,
        cache_key,
        LOCATION_CACHE_TTL,
        _location_cache_lock,
    )

    if cached is not None:

        print(
            "Location cache HIT:",
            cache_key,
        )

        return cached

    print(
        "Location cache MISS:",
        cache_key,
    )

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
                timeout=8,
            )

            results = data.get(
                "results",
                [],
            )

            if isinstance(results, list):

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
            ValueError,
        ):
            continue

        key = (
            round(latitude, 6),
            round(longitude, 6),
        )

        if key in seen:
            continue

        seen.add(key)

        # -------------------------------------------------
        # LOCATION INFORMATION
        # -------------------------------------------------

        name = item.get(
            "name",
            village,
        )

        country = item.get(
            "country",
            "India",
        )

        result_state = item.get(
            "admin1",
            "",
        )

        result_district = item.get(
            "admin2",
            "",
        )

        # -------------------------------------------------
        # DISPLAY NAME
        # -------------------------------------------------

        display_parts = [
            name,
            result_district,
            result_state,
            country,
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
                "timezone": item.get(
                    "timezone",
                    "",
                ),
                "display_name": display_name,
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
                "",
            )
            or ""
        )

        item_district = normalize_location_text(
            item.get(
                "district",
                "",
            )
            or ""
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
        reverse=True,
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
        final_results,
        _location_cache_lock,
    )

    return final_results


# =========================================================
# LOCATION COORDINATES
# =========================================================

def get_location_coordinates(
    location: str,
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
            "name": "Selected Location",
            "latitude": latitude,
            "longitude": longitude,
            "country": "India",
            "state": "",
            "district": "",
            "timezone": "",
            "display_name": (
                f"{latitude}, {longitude}"
            ),
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
        normalized_location,
    )

    cached = _get_cache(
        _location_cache,
        cache_key,
        LOCATION_CACHE_TTL,
        _location_cache_lock,
    )

    if cached is not None:

        print(
            "Location coordinate cache HIT:",
            normalized_location,
        )

        return cached

    print(
        "Location coordinate cache MISS:",
        normalized_location,
    )

    # =====================================================
    # CALL GEOCODING API
    # =====================================================

    try:

        data = _request_open_meteo(
            GEOCODING_URL,
            {
                "name": normalized_location,
                "count": 10,
                "language": "en",
                "format": "json",
            },
            timeout=10,
        )

    except Exception as exc:

        raise Exception(
            str(exc)
        ) from exc

    # =====================================================
    # RESULTS
    # =====================================================

    results = data.get(
        "results",
        [],
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
        ValueError,
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
        location,
    )

    country = result.get(
        "country",
        "",
    )

    state = result.get(
        "admin1",
        "",
    )

    district = result.get(
        "admin2",
        "",
    )

    # =====================================================
    # DISPLAY NAME
    # =====================================================

    display_parts = [
        name,
        district,
        state,
        country,
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
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "country": country,
        "state": state,
        "district": district,
        "timezone": result.get(
            "timezone",
            "",
        ),
        "display_name": display_name,
    }

    # =====================================================
    # CACHE
    # =====================================================

    _set_cache(
        _location_cache,
        cache_key,
        location_data,
        _location_cache_lock,
    )

    return location_data


# =========================================================
# CURRENT WEATHER
# =========================================================

def get_current_weather(
    latitude: float,
    longitude: float,
):
    """
    Get current weather and 7-day forecast.

    Weather data is cached for 10 minutes.

    If Open-Meteo temporarily fails after the cache
    expires, the previous cached result is returned
    when available.
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
        ValueError,
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
        longitude,
    )

    # =====================================================
    # CHECK FRESH CACHE
    # =====================================================

    cached = _get_cache(
        _weather_cache,
        cache_key,
        WEATHER_CACHE_TTL,
        _weather_cache_lock,
    )

    if cached is not None:

        print(
            "Weather cache HIT:",
            cache_key,
        )

        return cached

    print(
        "Weather cache MISS:",
        cache_key,
    )

    # =====================================================
    # REQUEST LOCK
    # =====================================================

    request_lock = _get_weather_request_lock(
        cache_key
    )

    # =====================================================
    # LOCK SAME-LOCATION REQUESTS
    # =====================================================

    with request_lock:

        # -------------------------------------------------
        # CHECK CACHE AGAIN
        # -------------------------------------------------
        #
        # Another request may have completed while this
        # request was waiting for the lock.
        # -------------------------------------------------

        cached = _get_cache(
            _weather_cache,
            cache_key,
            WEATHER_CACHE_TTL,
            _weather_cache_lock,
        )

        if cached is not None:

            print(
                "Weather cache HIT after "
                "request lock:",
                cache_key,
            )

            return cached

        # =================================================
        # WEATHER PARAMETERS
        # =================================================

        params = {
            "latitude": latitude,
            "longitude": longitude,
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
            "timezone": "auto",
            "forecast_days": 7,
        }

        # =================================================
        # REQUEST WEATHER
        # =================================================

        try:

            data = _request_open_meteo(
                WEATHER_URL,
                params,
                timeout=15,
            )

        except Exception as exc:

            # -------------------------------------------------
            # STALE CACHE FALLBACK
            # -------------------------------------------------

            stale_cached = _get_stale_cache(
                _weather_cache,
                cache_key,
                _weather_cache_lock,
            )

            if stale_cached is not None:

                print(
                    "Open-Meteo unavailable. "
                    "Returning stale weather cache:",
                    cache_key,
                )

                return stale_cached

            # -------------------------------------------------
            # NO CACHE AVAILABLE
            # -------------------------------------------------

            raise Exception(
                str(exc)
            ) from exc

        # =================================================
        # VALIDATE RESPONSE
        # =================================================

        if not isinstance(
            data,
            dict,
        ):

            raise Exception(
                "Invalid weather response "
                "received from Open-Meteo."
            )

        # =================================================
        # NORMALIZED RESPONSE
        # =================================================

        weather_data = {
            "latitude": data.get(
                "latitude"
            ),
            "longitude": data.get(
                "longitude"
            ),
            "timezone": data.get(
                "timezone"
            ),
            "current": data.get(
                "current",
                {},
            ),
            "forecast": data.get(
                "daily",
                {},
            ),
        }

        # =================================================
        # SAVE CACHE
        # =================================================

        _set_cache(
            _weather_cache,
            cache_key,
            weather_data,
            _weather_cache_lock,
        )

        print(
            "Weather cache UPDATED:",
            cache_key,
        )

        return weather_data


# =========================================================
# WEATHER BY LOCATION
# =========================================================

def get_weather_for_location(
    location: str,
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
            location_data["latitude"],
            location_data["longitude"],
        )
    )

    # -----------------------------------------------------
    # Do not modify the cached weather object directly.
    # -----------------------------------------------------

    result = dict(
        weather_data
    )

    result["location"] = location_data

    return result


# =========================================================
# WEATHER BY COORDINATES
# =========================================================

def get_weather_by_coordinates(
    latitude: float,
    longitude: float,
):
    """
    Get weather directly using coordinates.

    No geocoding request is performed.
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
        ValueError,
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
            longitude,
        )
    )

    # =====================================================
    # ATTACH LOCATION
    # =====================================================

    result = dict(
        weather_data
    )

    result["location"] = {
        "name": "Selected Location",
        "latitude": latitude,
        "longitude": longitude,
        "country": "India",
    }

    return result