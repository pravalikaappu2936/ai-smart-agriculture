import re
import time
import threading
from datetime import datetime
from typing import Optional, Tuple

import requests


# =========================================================
# WEATHER API URLS
# =========================================================

# Primary provider
GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
)

# Fallback provider
# MET Norway Locationforecast 2.0
MET_WEATHER_URL = (
    "https://api.met.no/weatherapi/locationforecast/2.0/compact"
)


# =========================================================
# CACHE SETTINGS
# =========================================================

# Keep weather data for 15 minutes.
WEATHER_CACHE_TTL = 900

# Location/geocoding data for 1 hour.
LOCATION_CACHE_TTL = 3600

# Only retry Open-Meteo once.
MAX_RETRIES = 1

# Maximum Retry-After wait.
MAX_RETRY_WAIT = 10


# =========================================================
# IN-MEMORY CACHE
# =========================================================

_weather_cache = {}
_location_cache = {}


# =========================================================
# CACHE LOCKS
# =========================================================

_weather_cache_lock = threading.Lock()
_location_cache_lock = threading.Lock()


# =========================================================
# WEATHER REQUEST LOCKS
# =========================================================

_weather_request_locks = {}
_weather_request_locks_lock = threading.Lock()


# =========================================================
# HTTP SESSION
# =========================================================

session = requests.Session()

session.headers.update(
    {
        "User-Agent": (
            "AI-Smart-Agriculture/1.0 "
            "https://github.com/"
        )
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

    All become the same normalized value.
    """

    if value is None:
        return ""

    return " ".join(
        str(value).strip().split()
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
        latitude = float(match.group(1))
        longitude = float(match.group(2))
    except ValueError:
        return None

    if latitude < -90 or latitude > 90:
        return None

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
                cache.pop(key, None)
        else:
            cache.pop(key, None)

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
    Return cached data even if it has expired.

    This is important when an external weather API
    temporarily returns 429 or 5xx.
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
    Round coordinates so tiny GPS differences don't
    create unnecessary API requests.
    """

    return (
        round(float(latitude), 3),
        round(float(longitude), 3),
    )


# =========================================================
# WEATHER REQUEST LOCK
# =========================================================

def _get_weather_request_lock(key):

    with _weather_request_locks_lock:

        lock = _weather_request_locks.get(key)

        if lock is None:
            lock = threading.Lock()
            _weather_request_locks[key] = lock

        return lock


# =========================================================
# OPEN-METEO REQUEST
# =========================================================

def _request_open_meteo(
    url: str,
    params: dict,
    timeout: int = 15,
):
    """
    Request Open-Meteo.

    429 is retried only once.
    """

    last_error = None

    for attempt in range(MAX_RETRIES + 1):

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
                    wait_seconds = 5

                wait_seconds = min(
                    wait_seconds,
                    MAX_RETRY_WAIT,
                )

                last_error = (
                    "Open-Meteo returned "
                    "429 Too Many Requests."
                )

                print(
                    "Open-Meteo rate limit "
                    f"(attempt {attempt + 1}/"
                    f"{MAX_RETRIES + 1}). "
                    f"Waiting {wait_seconds:.0f}s."
                )

                if attempt < MAX_RETRIES:
                    time.sleep(wait_seconds)
                    continue

                raise Exception(last_error)

            # =================================================
            # OTHER HTTP ERRORS
            # =================================================

            response.raise_for_status()

            return response.json()

        except requests.Timeout as exc:

            last_error = (
                "Open-Meteo request timed out."
            )

            print(
                "Open-Meteo timeout:",
                exc,
            )

            if attempt < MAX_RETRIES:
                time.sleep(2)
                continue

            raise Exception(
                last_error
            ) from exc

        except requests.HTTPError as exc:

            last_error = (
                f"Open-Meteo HTTP error: {exc}"
            )

            print(
                "Open-Meteo HTTP error:",
                exc,
            )

            raise Exception(
                last_error
            ) from exc

        except requests.RequestException as exc:

            last_error = (
                f"Open-Meteo request error: {exc}"
            )

            print(
                "Open-Meteo request error:",
                exc,
            )

            if attempt < MAX_RETRIES:
                time.sleep(2)
                continue

            raise Exception(
                last_error
            ) from exc

        except ValueError as exc:

            raise Exception(
                "Invalid response received "
                "from Open-Meteo."
            ) from exc

    raise Exception(
        last_error
        or "Unable to connect to Open-Meteo."
    )


# =========================================================
# MET NORWAY FALLBACK
# =========================================================

def _request_met_norway(
    latitude: float,
    longitude: float,
    timeout: int = 15,
):
    """
    Fallback weather provider.

    MET Norway provides global Locationforecast
    data using latitude and longitude.
    """

    # MET Norway recommends no more than 4 decimals
    # for efficient caching.
    latitude = round(float(latitude), 4)
    longitude = round(float(longitude), 4)

    params = {
        "lat": latitude,
        "lon": longitude,
    }

    print(
        "Trying MET Norway fallback:",
        latitude,
        longitude,
    )

    fallback_headers = {
        "User-Agent": (
            "AI-Smart-Agriculture/1.0 "
            "https://github.com/"
        ),
        "Accept": "application/json",
    }

    try:

        response = session.get(
            MET_WEATHER_URL,
            params=params,
            headers=fallback_headers,
            timeout=timeout,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            raise Exception(
                "Invalid response from MET Norway."
            )

        return data

    except requests.HTTPError as exc:

        print(
            "MET Norway HTTP error:",
            exc,
        )

        raise Exception(
            f"MET Norway weather service error: {exc}"
        ) from exc

    except requests.RequestException as exc:

        print(
            "MET Norway request error:",
            exc,
        )

        raise Exception(
            "Unable to connect to MET Norway weather service."
        ) from exc

    except ValueError as exc:

        raise Exception(
            "Invalid response received from MET Norway."
        ) from exc


# =========================================================
# CONVERT MET NORWAY WEATHER
# =========================================================

def _convert_met_norway_weather(
    data: dict,
    latitude: float,
    longitude: float,
):
    """
    Convert MET Norway response into the same structure
    used by the existing React frontend.
    """

    properties = data.get(
        "properties",
        {},
    )

    timeseries = properties.get(
        "timeseries",
        [],
    )

    if not isinstance(timeseries, list):
        timeseries = []

    if not timeseries:
        raise Exception(
            "MET Norway returned no forecast data."
        )

    # =====================================================
    # FIND CURRENT / NEAREST FORECAST
    # =====================================================

    now = datetime.utcnow()

    selected = None

    for item in timeseries:

        time_string = item.get(
            "time"
        )

        if not time_string:
            continue

        try:

            item_time = datetime.fromisoformat(
                time_string.replace(
                    "Z",
                    "+00:00",
                )
            ).replace(
                tzinfo=None
            )

        except ValueError:
            continue

        if item_time >= now:
            selected = item
            break

    if selected is None:
        selected = timeseries[0]

    instant = (
        selected
        .get("data", {})
        .get("instant", {})
        .get("details", {})
    )

    next_1_hours = (
        selected
        .get("data", {})
        .get("next_1_hours", {})
        .get("details", {})
    )

    # =====================================================
    # CURRENT VALUES
    # =====================================================

    temperature = instant.get(
        "air_temperature"
    )

    humidity = instant.get(
        "relative_humidity"
    )

    wind_speed = instant.get(
        "wind_speed"
    )

    precipitation = next_1_hours.get(
        "precipitation_amount",
        0,
    )

    # =====================================================
    # BUILD CURRENT RESPONSE
    # =====================================================

    current = {
        "time": selected.get(
            "time"
        ),
        "temperature_2m": temperature,
        "relative_humidity_2m": humidity,
        "precipitation": precipitation,
        "rain": precipitation,
        "weather_code": None,
        "wind_speed_10m": wind_speed,
    }

    # =====================================================
    # BUILD DAILY FORECAST
    # =====================================================

    daily = {
        "time": [],
        "temperature_2m_max": [],
        "temperature_2m_min": [],
        "precipitation_probability_max": [],
        "weather_code": [],
        "wind_speed_10m_max": [],
    }

    # Group available timeseries by date.
    daily_items = {}

    for item in timeseries:

        time_string = item.get(
            "time"
        )

        if not time_string:
            continue

        try:

            date_string = (
                time_string
                .split("T")[0]
            )

        except Exception:
            continue

        daily_items.setdefault(
            date_string,
            [],
        ).append(item)

    for date_string, items in list(
        daily_items.items()
    )[:7]:

        temperatures = []
        wind_values = []
        precipitation_values = []

        for item in items:

            details = (
                item
                .get("data", {})
                .get("instant", {})
                .get("details", {})
            )

            temp = details.get(
                "air_temperature"
            )

            wind = details.get(
                "wind_speed"
            )

            if isinstance(
                temp,
                (int, float),
            ):
                temperatures.append(temp)

            if isinstance(
                wind,
                (int, float),
            ):
                wind_values.append(wind)

            precipitation_details = (
                item
                .get("data", {})
                .get("next_1_hours", {})
                .get("details", {})
            )

            precipitation_value = (
                precipitation_details.get(
                    "precipitation_amount"
                )
            )

            if isinstance(
                precipitation_value,
                (int, float),
            ):
                precipitation_values.append(
                    precipitation_value
                )

        daily["time"].append(
            date_string
        )

        daily["temperature_2m_max"].append(
            max(temperatures)
            if temperatures
            else None
        )

        daily["temperature_2m_min"].append(
            min(temperatures)
            if temperatures
            else None
        )

        daily[
            "precipitation_probability_max"
        ].append(None)

        daily["weather_code"].append(None)

        daily["wind_speed_10m_max"].append(
            max(wind_values)
            if wind_values
            else None
        )

    return {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": "auto",
        "current": current,
        "forecast": daily,
    }


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
    """

    village = normalize_location_text(village)
    district = normalize_location_text(district)
    state = normalize_location_text(state)

    if not village:
        return []

    coordinates = parse_coordinates(village)

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
                all_results.extend(results)

            indian_results = [
                item
                for item in all_results
                if item.get(
                    "country_code"
                ) == "IN"
            ]

            if len(indian_results) >= 5:
                break

    except Exception as exc:

        raise Exception(
            str(exc)
        ) from exc

    india_results = [
        item
        for item in all_results
        if item.get(
            "country_code"
        ) == "IN"
    ]

    if not india_results:
        india_results = all_results

    unique_results = []
    seen = set()

    for item in india_results:

        latitude = item.get("latitude")
        longitude = item.get("longitude")

        if (
            latitude is None
            or longitude is None
        ):
            continue

        try:

            latitude = float(latitude)
            longitude = float(longitude)

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

    def result_score(item):

        score = 0

        item_state = normalize_location_text(
            item.get("state", "") or ""
        )

        item_district = normalize_location_text(
            item.get("district", "") or ""
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

    unique_results.sort(
        key=result_score,
        reverse=True,
    )

    final_results = unique_results[:8]

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
    Convert location name into coordinates.
    """

    if (
        not location
        or not str(location).strip()
    ):
        raise ValueError(
            "Location cannot be empty."
        )

    location = str(location).strip()

    coordinates = parse_coordinates(location)

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

    normalized_location = normalize_location_text(
        location
    )

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

    results = data.get(
        "results",
        [],
    )

    if not results:
        raise ValueError(
            f"Location '{location}' could not be found."
        )

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

        latitude = float(latitude)
        longitude = float(longitude)

    except (
        TypeError,
        ValueError,
    ):

        raise ValueError(
            "Invalid coordinates returned "
            "by location service."
        )

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
    Get current weather and forecast.

    Primary:
        Open-Meteo

    Fallback:
        MET Norway

    Cache:
        15 minutes
    """

    try:

        latitude = float(latitude)
        longitude = float(longitude)

    except (
        TypeError,
        ValueError,
    ):

        raise ValueError(
            "Invalid latitude or longitude."
        )

    if latitude < -90 or latitude > 90:

        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    if longitude < -180 or longitude > 180:

        raise ValueError(
            "Longitude must be between -180 and 180."
        )

    cache_key = _weather_cache_key(
        latitude,
        longitude,
    )

    # =====================================================
    # FRESH CACHE
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

    request_lock = _get_weather_request_lock(
        cache_key
    )

    with request_lock:

        # =================================================
        # CHECK CACHE AGAIN
        # =================================================

        cached = _get_cache(
            _weather_cache,
            cache_key,
            WEATHER_CACHE_TTL,
            _weather_cache_lock,
        )

        if cached is not None:

            print(
                "Weather cache HIT after request lock:",
                cache_key,
            )

            return cached

        # =================================================
        # OPEN-METEO PARAMETERS
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
        # TRY OPEN-METEO
        # =================================================

        try:

            data = _request_open_meteo(
                WEATHER_URL,
                params,
                timeout=15,
            )

            print(
                "Open-Meteo weather request successful."
            )

        except Exception as open_meteo_error:

            print(
                "Open-Meteo unavailable:",
                open_meteo_error,
            )

            # =================================================
            # TRY MET NORWAY
            # =================================================

            try:

                met_data = _request_met_norway(
                    latitude,
                    longitude,
                    timeout=15,
                )

                weather_data = (
                    _convert_met_norway_weather(
                        met_data,
                        latitude,
                        longitude,
                    )
                )

                _set_cache(
                    _weather_cache,
                    cache_key,
                    weather_data,
                    _weather_cache_lock,
                )

                print(
                    "Weather cache UPDATED "
                    "using MET Norway fallback:",
                    cache_key,
                )

                return weather_data

            except Exception as fallback_error:

                print(
                    "MET Norway fallback failed:",
                    fallback_error,
                )

                # =================================================
                # STALE CACHE
                # =================================================

                stale_cached = _get_stale_cache(
                    _weather_cache,
                    cache_key,
                    _weather_cache_lock,
                )

                if stale_cached is not None:

                    print(
                        "Returning stale weather cache:",
                        cache_key,
                    )

                    return stale_cached

                raise Exception(
                    "Weather services are temporarily "
                    "unavailable. Please try again shortly."
                ) from fallback_error

        # =================================================
        # VALIDATE OPEN-METEO RESPONSE
        # =================================================

        if not isinstance(data, dict):

            raise Exception(
                "Invalid weather response received "
                "from Open-Meteo."
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

    location_data = get_location_coordinates(
        location
    )

    weather_data = get_current_weather(
        location_data["latitude"],
        location_data["longitude"],
    )

    result = dict(weather_data)

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

    try:

        latitude = float(latitude)
        longitude = float(longitude)

    except (
        TypeError,
        ValueError,
    ):

        raise ValueError(
            "Invalid latitude or longitude."
        )

    if latitude < -90 or latitude > 90:

        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    if longitude < -180 or longitude > 180:

        raise ValueError(
            "Longitude must be between -180 and 180."
        )

    weather_data = get_current_weather(
        latitude,
        longitude,
    )

    result = dict(weather_data)

    result["location"] = {
        "name": "Selected Location",
        "latitude": latitude,
        "longitude": longitude,
        "country": "India",
    }

    return result