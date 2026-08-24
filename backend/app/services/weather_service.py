import re
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
# NORMALIZE LOCATION TEXT
# =========================================================

def normalize_location_text(value: str) -> str:
    """
    Normalize location input so that capitalization does not
    affect the search.

    Examples:

        Karnataka
        karnataka
        KARNATAKA
        KaRnAtAkA

    All are normalized to the same search value.

    Extra spaces are also removed.
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

def parse_coordinates(location: str):
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
    # Match:
    # latitude, longitude
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
    # Validate latitude
    # -----------------------------------------------------

    if latitude < -90 or latitude > 90:
        return None

    # -----------------------------------------------------
    # Validate longitude
    # -----------------------------------------------------

    if longitude < -180 or longitude > 180:
        return None

    return latitude, longitude


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

    The search is CASE-INSENSITIVE.

    Examples:

        Karnataka
        karnataka
        KARNATAKA

    are treated identically.

    Existing coordinate search functionality is preserved.
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
    # IF USER ENTERED COORDINATES
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
    # NORMAL LOCATION SEARCH
    # =====================================================

    search_queries = []

    # -----------------------------------------------------
    # Village + District + State
    # -----------------------------------------------------

    if district and state:

        search_queries.append(
            f"{village}, {district}, {state}, India"
        )

    # -----------------------------------------------------
    # Village + State
    # -----------------------------------------------------

    if state:

        search_queries.append(
            f"{village}, {state}, India"
        )

    # -----------------------------------------------------
    # Village + India
    # -----------------------------------------------------

    search_queries.append(
        f"{village}, India"
    )

    all_results = []

    # =====================================================
    # CALL OPEN-METEO
    # =====================================================

    try:

        for query in search_queries:

            response = requests.get(

                GEOCODING_URL,

                params={
                    "name": query,

                    "count": 10,

                    "language": "en",

                    "format": "json",
                },

                timeout=8,
            )

            response.raise_for_status()

            data = response.json()

            results = data.get(
                "results",
                []
            )

            all_results.extend(
                results
            )

            # -------------------------------------------------
            # Check Indian results
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

    except requests.Timeout:

        raise Exception(
            "Location service timed out. Please try again."
        )

    except requests.RequestException as exc:

        raise Exception(
            f"Unable to connect to location service: {exc}"
        )

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
    # REMOVE DUPLICATE COORDINATES
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

        # -------------------------------------------------
        # ADD RESULT
        # -------------------------------------------------

        unique_results.append({

            "name":
                name,

            "latitude":
                latitude,

            "longitude":
                longitude,

            "country":
                country,

            "state":
                result_state,

            "district":
                result_district,

            "timezone":
                item.get(
                    "timezone",
                    ""
                ),

            "display_name":
                display_name,
        })

    # =====================================================
    # LOCATION RANKING
    # =====================================================

    def result_score(item):

        score = 0

        # -------------------------------------------------
        # Result state
        # -------------------------------------------------

        item_state = normalize_location_text(

            item.get(
                "state",
                ""
            )
            or ""

        )

        # -------------------------------------------------
        # Result district
        # -------------------------------------------------

        item_district = normalize_location_text(

            item.get(
                "district",
                ""
            )
            or ""

        )

        # -------------------------------------------------
        # Requested values
        # -------------------------------------------------

        requested_state = normalize_location_text(
            state
        )

        requested_district = normalize_location_text(
            district
        )

        # -------------------------------------------------
        # State match
        # -------------------------------------------------

        if requested_state:

            if requested_state in item_state:

                score += 20

        # -------------------------------------------------
        # District match
        # -------------------------------------------------

        if requested_district:

            if requested_district in item_district:

                score += 30

        return score

    # =====================================================
    # SORT RESULTS
    # =====================================================

    unique_results.sort(

        key=result_score,

        reverse=True

    )

    # =====================================================
    # RETURN MAX 8 RESULTS
    # =====================================================

    return unique_results[:8]


# =========================================================
# LOCATION COORDINATES
# =========================================================

def get_location_coordinates(
    location: str
):
    """
    Convert a location name into latitude and longitude.

    Location search is case-insensitive.
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
    # NORMALIZE LOCATION NAME
    # =====================================================

    normalized_location = normalize_location_text(
        location
    )

    # =====================================================
    # NORMAL LOCATION NAME
    # =====================================================

    try:

        response = requests.get(

            GEOCODING_URL,

            params={

                "name":
                    normalized_location,

                "count":
                    10,

                "language":
                    "en",

                "format":
                    "json",
            },

            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

    except requests.Timeout:

        raise Exception(
            "Location service timed out. Please try again."
        )

    except requests.RequestException as exc:

        raise Exception(
            f"Unable to connect to location service: {exc}"
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
    # GET COORDINATES
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
            "Coordinates were not available for this location."
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
            "Invalid coordinates returned by location service."
        )

    # =====================================================
    # VALIDATE COORDINATES
    # =====================================================

    if latitude < -90 or latitude > 90:

        raise ValueError(
            "Invalid latitude returned by location service."
        )

    if longitude < -180 or longitude > 180:

        raise ValueError(
            "Invalid longitude returned by location service."
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
    # RETURN LOCATION
    # =====================================================

    return {

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


# =========================================================
# CURRENT WEATHER
# =========================================================

def get_current_weather(
    latitude: float,
    longitude: float
):
    """
    Get current weather and 7-day forecast.
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
    # VALIDATE COORDINATES
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
    # REQUEST WEATHER
    # =====================================================

    try:

        response = requests.get(

            WEATHER_URL,

            params={

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
            },

            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

    except requests.Timeout:

        raise Exception(
            "Weather service timed out. Please try again."
        )

    except requests.RequestException as exc:

        raise Exception(
            f"Unable to connect to weather service: {exc}"
        )

    # =====================================================
    # RETURN NORMALIZED WEATHER RESPONSE
    # =====================================================

    return {

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


# =========================================================
# WEATHER BY LOCATION
# =========================================================

def get_weather_for_location(
    location: str
):
    """
    Get weather using a location name.

    Location capitalization does not matter.
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
    # CONVERT TO FLOAT
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
    # VALIDATE COORDINATES
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
    # GET WEATHER
    # =====================================================

    weather_data = (
        get_current_weather(

            latitude,

            longitude

        )
    )

    # =====================================================
    # ATTACH LOCATION INFORMATION
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