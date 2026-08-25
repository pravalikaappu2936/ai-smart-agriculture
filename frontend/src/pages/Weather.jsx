import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
    MapContainer,
    TileLayer,
    useMap,
    Marker,
} from "react-leaflet";

import L from "leaflet";

import "leaflet/dist/leaflet.css";
import "./Weather.css";


// ============================================================
// API
// ============================================================

const API_URL =
    import.meta.env.VITE_API_URL ||
    "https://ai-smart-agriculture-jf61.onrender.com";


// ============================================================
// LEAFLET MARKER FIX
// ============================================================

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
    iconRetinaUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",

    iconUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",

    shadowUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});


// ============================================================
// TRANSLATIONS
// ============================================================

const translations = {
    en: {
        backDashboard: "← Back to Dashboard",

        title: "Weather",
        subtitle: "Monitor weather conditions for your farm",

        enterFarmLocation: "📍 Enter Farm Location",
        enterLocationDescription:
            "Enter your State, District and Village/Town/City.",

        state: "State",
        district: "District",
        villageTownCity: "Village / Town / City",

        statePlaceholder: "Example: Karnataka",
        districtPlaceholder: "Example: Mysuru",
        villagePlaceholder: "Type your village name",

        searching: "🔍 Searching locations...",
        locationSelected: "✓ Location selected",

        loading: "Loading...",
        getWeather: "🔍 Get Weather",

        selectFarmMap: "🗺️ Select Farm Location From Map",

        mapDescription:
            "Move the map and place the farm under the crosshair.",

        mapInstruction:
            "Move the map to position your farm under the crosshair",

        mapCenter: "📍 Map Center",

        latitude: "Latitude",
        longitude: "Longitude",

        selectCenter: "📍 Select Center Location",

        selectedFarmLocation:
            "Selected Farm Location",

        getMapWeather: "🌦️ Get Weather",

        useMyLocation: "📍 Use My Location",

        detectingLocation:
            "Detecting Location...",

        currentWeather: "Current Weather",

        temperature: "🌡️ Temperature",
        humidity: "💧 Humidity",
        rainfall: "🌧️ Rainfall",
        windSpeed: "💨 Wind Speed",

        forecast: "📅 7-Day Forecast",

        rain: "rain",

        agriculturalInsight:
            "🌾 Agricultural Insight",

        loadingWeather:
            "Loading weather information...",

        selectedLocation:
            "Selected Location",

        locationSearchFailed:
            "Location search failed.",

        unableWeather:
            "Unable to fetch weather.",

        enterState:
            "Please enter the state.",

        enterDistrict:
            "Please enter the district.",

        enterVillage:
            "Please enter the village, town or city.",

        selectMapFirst:
            "Please select a location on the map first.",

        geolocationNotSupported:
            "Geolocation is not supported by your browser.",

        locationPermission:
            "Unable to access your location. Please allow location permission.",

        clearSky: "Clear sky",
        mainlyClear: "Mainly clear",
        partlyCloudy: "Partly cloudy",
        overcast: "Overcast",

        fog: "Fog",
        rimeFog: "Rime fog",

        lightDrizzle: "Light drizzle",
        moderateDrizzle: "Moderate drizzle",
        denseDrizzle: "Dense drizzle",

        slightRain: "Slight rain",
        moderateRain: "Moderate rain",
        heavyRain: "Heavy rain",

        slightSnowfall: "Slight snowfall",
        moderateSnowfall: "Moderate snowfall",
        heavySnowfall: "Heavy snowfall",

        slightRainShowers: "Slight rain showers",
        moderateRainShowers: "Moderate rain showers",
        heavyRainShowers: "Heavy rain showers",

        thunderstorm: "Thunderstorm",

        thunderstormHail:
            "Thunderstorm with hail",

        thunderstormHeavyHail:
            "Thunderstorm with heavy hail",

        weatherInformation:
            "Weather information",

        insightSelectLocation:
            "Select a location to view agricultural insights.",

        insightRain:
            "Rainfall is significant. Consider reducing irrigation and monitor field drainage.",

        insightHumidity:
            "High humidity is present. Monitor crops for fungal diseases and avoid unnecessary irrigation.",

        insightHot:
            "High temperatures may increase crop water requirements. Monitor soil moisture and irrigate when necessary.",

        insightCold:
            "Cool temperatures are present. Monitor crop growth and avoid excessive irrigation.",

        insightNormal:
            "Weather conditions appear suitable for farming. Continue monitoring soil moisture and weather changes.",

        na: "N/A",
    },

    kn: {
        backDashboard: "← ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗೆ ಹಿಂತಿರುಗಿ",

        title: "ಹವಾಮಾನ",

        subtitle:
            "ನಿಮ್ಮ ಕೃಷಿ ಜಮೀನಿನ ಹವಾಮಾನ ಪರಿಸ್ಥಿತಿಗಳನ್ನು ಮೇಲ್ವಿಚಾರಣೆ ಮಾಡಿ",

        enterFarmLocation:
            "📍 ಕೃಷಿ ಜಮೀನಿನ ಸ್ಥಳ ನಮೂದಿಸಿ",

        enterLocationDescription:
            "ನಿಮ್ಮ ರಾಜ್ಯ, ಜಿಲ್ಲೆ ಮತ್ತು ಗ್ರಾಮ/ಪಟ್ಟಣ/ನಗರವನ್ನು ನಮೂದಿಸಿ.",

        state: "ರಾಜ್ಯ",

        district: "ಜಿಲ್ಲೆ",

        villageTownCity:
            "ಗ್ರಾಮ / ಪಟ್ಟಣ / ನಗರ",

        statePlaceholder:
            "ಉದಾಹರಣೆ: ಕರ್ನಾಟಕ",

        districtPlaceholder:
            "ಉದಾಹರಣೆ: ಮೈಸೂರು",

        villagePlaceholder:
            "ನಿಮ್ಮ ಗ್ರಾಮದ ಹೆಸರನ್ನು ನಮೂದಿಸಿ",

        searching:
            "🔍 ಸ್ಥಳಗಳನ್ನು ಹುಡುಕಲಾಗುತ್ತಿದೆ...",

        locationSelected:
            "✓ ಸ್ಥಳ ಆಯ್ಕೆ ಮಾಡಲಾಗಿದೆ",

        loading:
            "ಲೋಡ್ ಆಗುತ್ತಿದೆ...",

        getWeather:
            "🔍 ಹವಾಮಾನ ಪಡೆಯಿರಿ",

        selectFarmMap:
            "🗺️ ನಕ್ಷೆಯಿಂದ ಕೃಷಿ ಜಮೀನಿನ ಸ್ಥಳ ಆಯ್ಕೆಮಾಡಿ",

        mapDescription:
            "ನಕ್ಷೆಯನ್ನು ಸರಿಸಿ ಮತ್ತು ಕ್ರಾಸ್‌ಹೇರ್ ಕೆಳಗೆ ಜಮೀನನ್ನು ಇರಿಸಿ.",

        mapInstruction:
            "ಕ್ರಾಸ್‌ಹೇರ್ ಕೆಳಗೆ ನಿಮ್ಮ ಜಮೀನನ್ನು ಇರಿಸಲು ನಕ್ಷೆಯನ್ನು ಸರಿಸಿ",

        mapCenter:
            "📍 ನಕ್ಷೆಯ ಕೇಂದ್ರ",

        latitude:
            "ಅಕ್ಷಾಂಶ",

        longitude:
            "ರೇಖಾಂಶ",

        selectCenter:
            "📍 ಕೇಂದ್ರ ಸ್ಥಳವನ್ನು ಆಯ್ಕೆಮಾಡಿ",

        selectedFarmLocation:
            "ಆಯ್ಕೆ ಮಾಡಿದ ಕೃಷಿ ಜಮೀನಿನ ಸ್ಥಳ",

        getMapWeather:
            "🌦️ ಹವಾಮಾನ ಪಡೆಯಿರಿ",

        useMyLocation:
            "📍 ನನ್ನ ಸ್ಥಳ ಬಳಸಿ",

        detectingLocation:
            "ಸ್ಥಳವನ್ನು ಪತ್ತೆಹಚ್ಚಲಾಗುತ್ತಿದೆ...",

        currentWeather:
            "ಪ್ರಸ್ತುತ ಹವಾಮಾನ",

        temperature:
            "🌡️ ತಾಪಮಾನ",

        humidity:
            "💧 ಆರ್ದ್ರತೆ",

        rainfall:
            "🌧️ ಮಳೆ",

        windSpeed:
            "💨 ಗಾಳಿಯ ವೇಗ",

        forecast:
            "📅 7 ದಿನಗಳ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ",

        rain:
            "ಮಳೆ",

        agriculturalInsight:
            "🌾 ಕೃಷಿ ಮಾಹಿತಿ",

        loadingWeather:
            "ಹವಾಮಾನ ಮಾಹಿತಿಯನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ...",

        selectedLocation:
            "ಆಯ್ಕೆ ಮಾಡಿದ ಸ್ಥಳ",

        locationSearchFailed:
            "ಸ್ಥಳ ಹುಡುಕುವಲ್ಲಿ ವಿಫಲವಾಗಿದೆ.",

        unableWeather:
            "ಹವಾಮಾನ ಮಾಹಿತಿಯನ್ನು ಪಡೆಯಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",

        enterState:
            "ದಯವಿಟ್ಟು ರಾಜ್ಯವನ್ನು ನಮೂದಿಸಿ.",

        enterDistrict:
            "ದಯವಿಟ್ಟು ಜಿಲ್ಲೆಯನ್ನು ನಮೂದಿಸಿ.",

        enterVillage:
            "ದಯವಿಟ್ಟು ಗ್ರಾಮ, ಪಟ್ಟಣ ಅಥವಾ ನಗರವನ್ನು ನಮೂದಿಸಿ.",

        selectMapFirst:
            "ದಯವಿಟ್ಟು ಮೊದಲು ನಕ್ಷೆಯಲ್ಲಿ ಸ್ಥಳವನ್ನು ಆಯ್ಕೆಮಾಡಿ.",

        geolocationNotSupported:
            "ನಿಮ್ಮ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಸ್ಥಳ ಪತ್ತೆಹಚ್ಚುವಿಕೆ ಬೆಂಬಲಿತವಾಗಿಲ್ಲ.",

        locationPermission:
            "ನಿಮ್ಮ ಸ್ಥಳವನ್ನು ಪ್ರವೇಶಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಸ್ಥಳ ಅನುಮತಿಯನ್ನು ನೀಡಿ.",

        clearSky:
            "ಸ್ವಚ್ಛ ಆಕಾಶ",

        mainlyClear:
            "ಮುಖ್ಯವಾಗಿ ಸ್ವಚ್ಛ ಆಕಾಶ",

        partlyCloudy:
            "ಭಾಗಶಃ ಮೋಡ ಕವಿದಿದೆ",

        overcast:
            "ಮೋಡ ಕವಿದಿದೆ",

        fog:
            "ಮಂಜು",

        rimeFog:
            "ಹಿಮ ಮಂಜು",

        lightDrizzle:
            "ಲಘು ತುಂತುರು ಮಳೆ",

        moderateDrizzle:
            "ಮಧ್ಯಮ ತುಂತುರು ಮಳೆ",

        denseDrizzle:
            "ದಟ್ಟ ತುಂತುರು ಮಳೆ",

        slightRain:
            "ಲಘು ಮಳೆ",

        moderateRain:
            "ಮಧ್ಯಮ ಮಳೆ",

        heavyRain:
            "ಭಾರಿ ಮಳೆ",

        slightSnowfall:
            "ಲಘು ಹಿಮಪಾತ",

        moderateSnowfall:
            "ಮಧ್ಯಮ ಹಿಮಪಾತ",

        heavySnowfall:
            "ಭಾರಿ ಹಿಮಪಾತ",

        slightRainShowers:
            "ಲಘು ಮಳೆಯ ಸುರಿತ",

        moderateRainShowers:
            "ಮಧ್ಯಮ ಮಳೆಯ ಸುರಿತ",

        heavyRainShowers:
            "ಭಾರಿ ಮಳೆಯ ಸುರಿತ",

        thunderstorm:
            "ಗುಡುಗು ಸಹಿತ ಮಳೆ",

        thunderstormHail:
            "ಆಲಿಕಲ್ಲು ಸಹಿತ ಗುಡುಗು ಮಳೆ",

        thunderstormHeavyHail:
            "ಭಾರಿ ಆಲಿಕಲ್ಲು ಸಹಿತ ಗುಡುಗು ಮಳೆ",

        weatherInformation:
            "ಹವಾಮಾನ ಮಾಹಿತಿ",

        insightSelectLocation:
            "ಕೃಷಿ ಮಾಹಿತಿಯನ್ನು ನೋಡಲು ಸ್ಥಳವನ್ನು ಆಯ್ಕೆಮಾಡಿ.",

        insightRain:
            "ಮಳೆಯ ಪ್ರಮಾಣ ಹೆಚ್ಚಾಗಿದೆ. ನೀರಾವರಿಯನ್ನು ಕಡಿಮೆ ಮಾಡಿ ಮತ್ತು ಜಮೀನಿನ ನೀರು ಹರಿವನ್ನು ಗಮನಿಸಿ.",

        insightHumidity:
            "ಆರ್ದ್ರತೆ ಹೆಚ್ಚಾಗಿದೆ. ಬೆಳೆಗಳಲ್ಲಿ ಶಿಲೀಂಧ್ರ ರೋಗಗಳನ್ನು ಗಮನಿಸಿ ಮತ್ತು ಅಗತ್ಯವಿಲ್ಲದ ನೀರಾವರಿಯನ್ನು ತಪ್ಪಿಸಿ.",

        insightHot:
            "ಹೆಚ್ಚಿನ ತಾಪಮಾನವು ಬೆಳೆಗಳ ನೀರಿನ ಅಗತ್ಯವನ್ನು ಹೆಚ್ಚಿಸಬಹುದು. ಮಣ್ಣಿನ ತೇವಾಂಶವನ್ನು ಗಮನಿಸಿ ಮತ್ತು ಅಗತ್ಯವಿದ್ದಾಗ ನೀರಾವರಿ ಮಾಡಿ.",

        insightCold:
            "ಕಡಿಮೆ ತಾಪಮಾನವಿದೆ. ಬೆಳೆಗಳ ಬೆಳವಣಿಗೆಯನ್ನು ಗಮನಿಸಿ ಮತ್ತು ಅತಿಯಾದ ನೀರಾವರಿಯನ್ನು ತಪ್ಪಿಸಿ.",

        insightNormal:
            "ಹವಾಮಾನ ಪರಿಸ್ಥಿತಿಗಳು ಕೃಷಿಗೆ ಸೂಕ್ತವಾಗಿವೆ. ಮಣ್ಣಿನ ತೇವಾಂಶ ಮತ್ತು ಹವಾಮಾನ ಬದಲಾವಣೆಗಳನ್ನು ಗಮನಿಸುತ್ತಿರಿ.",

        na:
            "ಲಭ್ಯವಿಲ್ಲ",
    },
};


// ============================================================
// WEATHER DESCRIPTION
// ============================================================

const getWeatherDescription = (
    code,
    language
) => {
    const t = translations[language];

    const codes = {
        0: t.clearSky,
        1: t.mainlyClear,
        2: t.partlyCloudy,
        3: t.overcast,

        45: t.fog,
        48: t.rimeFog,

        51: t.lightDrizzle,
        53: t.moderateDrizzle,
        55: t.denseDrizzle,

        61: t.slightRain,
        63: t.moderateRain,
        65: t.heavyRain,

        71: t.slightSnowfall,
        73: t.moderateSnowfall,
        75: t.heavySnowfall,

        80: t.slightRainShowers,
        81: t.moderateRainShowers,
        82: t.heavyRainShowers,

        95: t.thunderstorm,
        96: t.thunderstormHail,
        99: t.thunderstormHeavyHail,
    };

    return (
        codes[code] ||
        t.weatherInformation
    );
};


// ============================================================
// WEATHER ICON
// ============================================================

const getWeatherIcon = (code) => {
    if (code === 0) {
        return "☀️";
    }

    if ([1, 2].includes(code)) {
        return "🌤️";
    }

    if (code === 3) {
        return "☁️";
    }

    if ([45, 48].includes(code)) {
        return "🌫️";
    }

    if (
        [
            51,
            53,
            55,
            61,
            63,
            65,
            80,
            81,
            82,
        ].includes(code)
    ) {
        return "🌧️";
    }

    if ([71, 73, 75].includes(code)) {
        return "❄️";
    }

    if ([95, 96, 99].includes(code)) {
        return "⛈️";
    }

    return "🌤️";
};


// ============================================================
// MAP CENTER TRACKER
// ============================================================

function MapCenterTracker({
    onCenterChange,
}) {
    const map = useMap();

    useEffect(() => {
        const updateCenter = () => {
            const center = map.getCenter();

            onCenterChange({
                latitude: center.lat,
                longitude: center.lng,
            });
        };

        map.on(
            "move",
            updateCenter
        );

        updateCenter();

        return () => {
            map.off(
                "move",
                updateCenter
            );
        };
    }, [
        map,
        onCenterChange,
    ]);

    return null;
}


// ============================================================
// MAP VIEW CONTROLLER
// ============================================================

function MapViewController({
    location,
}) {
    const map = useMap();

    useEffect(() => {
        if (!location) {
            return;
        }

        map.setView(
            [
                location.latitude,
                location.longitude,
            ],
            15,
            {
                animate: true,
            }
        );
    }, [
        location,
        map,
    ]);

    return null;
}


// ============================================================
// WEATHER COMPONENT
// ============================================================

function Weather() {
    const navigate = useNavigate();

    // ========================================================
    // LANGUAGE
    // ========================================================

    const [
        language,
        setLanguage,
    ] = useState("en");

    const t =
        translations[language];


    // ========================================================
    // MANUAL LOCATION
    // ========================================================

    const [
        state,
        setState,
    ] = useState("");

    const [
        district,
        setDistrict,
    ] = useState("");

    const [
        village,
        setVillage,
    ] = useState("");


    // ========================================================
    // LOCATION SEARCH
    // ========================================================

    const [
        locationResults,
        setLocationResults,
    ] = useState([]);

    const [
        searchingLocations,
        setSearchingLocations,
    ] = useState(false);

    const [
        selectedPlace,
        setSelectedPlace,
    ] = useState(null);


    // ========================================================
    // MAP
    // ========================================================

    const [
        mapCenter,
        setMapCenter,
    ] = useState({
        latitude: 20.5937,
        longitude: 78.9629,
    });

    const [
        selectedLocation,
        setSelectedLocation,
    ] = useState(null);


    // ========================================================
    // WEATHER
    // ========================================================

    const [
        weather,
        setWeather,
    ] = useState(null);

    const [
        loading,
        setLoading,
    ] = useState(false);

    const [
        locationLoading,
        setLocationLoading,
    ] = useState(false);

    const [
        error,
        setError,
    ] = useState("");


    // ========================================================
    // BACK TO DASHBOARD
    // ========================================================

    const handleBackToDashboard = () => {
        navigate("/dashboard");
    };


    // ========================================================
    // SEARCH LOCATION
    // ========================================================

    useEffect(() => {
        const searchVillage =
            async () => {
                const searchText =
                    village.trim();

                if (
                    searchText.length < 2
                ) {
                    setLocationResults([]);
                    return;
                }

                setSearchingLocations(
                    true
                );

                try {
                    const params =
                        new URLSearchParams();

                    params.set(
                        "village",
                        searchText
                    );

                    if (
                        district.trim()
                    ) {
                        params.set(
                            "district",
                            district.trim()
                        );
                    }

                    if (
                        state.trim()
                    ) {
                        params.set(
                            "state",
                            state.trim()
                        );
                    }

                    const response =
                        await fetch(
                            `${API_URL}/weather/search?${params.toString()}`
                        );

                    if (
                        !response.ok
                    ) {
                        throw new Error(
                            t.locationSearchFailed
                        );
                    }

                    const data =
                        await response.json();

                    setLocationResults(
                        data.results || []
                    );
                } catch (err) {
                    console.error(
                        "Location search error:",
                        err
                    );

                    setLocationResults([]);
                } finally {
                    setSearchingLocations(
                        false
                    );
                }
            };

        const timer =
            setTimeout(
                searchVillage,
                700
            );

        return () => {
            clearTimeout(timer);
        };
    }, [
        village,
        district,
        state,
        language,
        t.locationSearchFailed,
    ]);


    // ========================================================
    // SELECT SEARCH RESULT
    // ========================================================

    const handlePlaceSelect = (
        place
    ) => {
        setSelectedPlace(place);

        setVillage(
            place.name || ""
        );

        if (place.state) {
            setState(place.state);
        }

        if (place.district) {
            setDistrict(
                place.district
            );
        }

        const location = {
            latitude:
                Number(
                    place.latitude
                ),

            longitude:
                Number(
                    place.longitude
                ),
        };

        setSelectedLocation(
            location
        );

        setMapCenter(
            location
        );

        setLocationResults([]);

        setError("");
    };


    // ========================================================
    // FETCH WEATHER BY COORDINATES
    // ========================================================

    const fetchWeatherByCoordinates =
        async (
            latitude,
            longitude
        ) => {
            setLoading(true);
            setError("");

            try {
                const token =
                    localStorage.getItem(
                        "token"
                    );

                const response =
                    await fetch(
                        `${API_URL}/weather/current-by-coordinates`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                ...(token
                                    ? {
                                          Authorization:
                                              `Bearer ${token}`,
                                      }
                                    : {}),
                            },

                            body:
                                JSON.stringify(
                                    {
                                        latitude:
                                            Number(
                                                latitude
                                            ),

                                        longitude:
                                            Number(
                                                longitude
                                            ),
                                    }
                                ),
                        }
                    );

                let data;

                try {
                    data =
                        await response.json();
                } catch {
                    data = {};
                }

                if (
                    !response.ok
                ) {
                    throw new Error(
                        data.detail ||
                            t.unableWeather
                    );
                }

                setWeather(data);
            } catch (err) {
                console.error(
                    "Coordinate weather error:",
                    err
                );

                setWeather(null);

                setError(
                    err.message ||
                        t.unableWeather
                );
            } finally {
                setLoading(false);
            }
        };


    // ========================================================
    // MANUAL WEATHER
    // ========================================================

    const handleManualWeather =
        async (event) => {
            event.preventDefault();

            setError("");
            setWeather(null);

            if (!state.trim()) {
                setError(
                    t.enterState
                );
                return;
            }

            if (!district.trim()) {
                setError(
                    t.enterDistrict
                );
                return;
            }

            if (!village.trim()) {
                setError(
                    t.enterVillage
                );
                return;
            }

            if (
                selectedPlace &&
                selectedPlace.latitude !==
                    undefined &&
                selectedPlace.longitude !==
                    undefined
            ) {
                await fetchWeatherByCoordinates(
                    selectedPlace.latitude,
                    selectedPlace.longitude
                );

                return;
            }

            setLoading(true);

            try {
                const location = [
                    village.trim(),
                    district.trim(),
                    state.trim(),
                    "India",
                ].join(", ");

                console.log(
                    "Sending location:",
                    location
                );

                const token =
                    localStorage.getItem(
                        "token"
                    );

                const response =
                    await fetch(
                        `${API_URL}/weather/current`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                ...(token
                                    ? {
                                          Authorization:
                                              `Bearer ${token}`,
                                      }
                                    : {}),
                            },

                            body:
                                JSON.stringify(
                                    {
                                        location,
                                    }
                                ),
                        }
                    );

                let data;

                try {
                    data =
                        await response.json();
                } catch {
                    data = {};
                }

                console.log(
                    "Manual weather response:",
                    data
                );

                if (
                    !response.ok
                ) {
                    throw new Error(
                        data.detail ||
                            t.unableWeather
                    );
                }

                setWeather(data);

                if (
                    data.location &&
                    data.location.latitude !==
                        undefined &&
                    data.location.longitude !==
                        undefined
                ) {
                    const locationData =
                        {
                            latitude:
                                Number(
                                    data.location.latitude
                                ),

                            longitude:
                                Number(
                                    data.location.longitude
                                ),
                        };

                    setSelectedLocation(
                        locationData
                    );

                    setMapCenter(
                        locationData
                    );
                }
            } catch (err) {
                console.error(
                    "Manual weather error:",
                    err
                );

                setWeather(null);

                setError(
                    err.message ||
                        t.unableWeather
                );
            } finally {
                setLoading(false);
            }
        };


    // ========================================================
    // SELECT MAP CENTER
    // ========================================================

    const handleSelectMapCenter =
        () => {
            const selected = {
                latitude:
                    mapCenter.latitude,

                longitude:
                    mapCenter.longitude,
            };

            setSelectedLocation(
                selected
            );

            setSelectedPlace(null);

            setError("");
        };


    // ========================================================
    // MAP WEATHER
    // ========================================================

    const handleMapWeather =
        async () => {
            if (!selectedLocation) {
                setError(
                    t.selectMapFirst
                );

                return;
            }

            await fetchWeatherByCoordinates(
                selectedLocation.latitude,
                selectedLocation.longitude
            );
        };


    // ========================================================
    // USE MY LOCATION
    // ========================================================

    const handleUseMyLocation =
        () => {
            if (
                !navigator.geolocation
            ) {
                setError(
                    t.geolocationNotSupported
                );

                return;
            }

            setLocationLoading(true);
            setError("");

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const location =
                        {
                            latitude:
                                position.coords
                                    .latitude,

                            longitude:
                                position.coords
                                    .longitude,
                        };

                    setMapCenter(
                        location
                    );

                    setSelectedLocation(
                        location
                    );

                    setSelectedPlace(
                        null
                    );

                    setLocationLoading(
                        false
                    );
                },

                (geoError) => {
                    console.error(
                        "Geolocation error:",
                        geoError
                    );

                    setError(
                        t.locationPermission
                    );

                    setLocationLoading(
                        false
                    );
                },

                {
                    enableHighAccuracy:
                        true,

                    timeout: 15000,

                    maximumAge: 0,
                }
            );
        };


    // ========================================================
    // WEATHER DATA
    // ========================================================

    const current =
        weather?.current || {};

    const forecast =
        weather?.forecast || {};

    const temperature =
        current.temperature_2m ??
        current.temperature;

    const humidity =
        current.relative_humidity_2m ??
        current.humidity;

    const windSpeed =
        current.wind_speed_10m ??
        current.wind_speed;

    const precipitation =
        current.precipitation ??
        current.rain ??
        0;

    const weatherCode =
        current.weather_code ??
        current.weathercode;


    // ========================================================
    // FORECAST DATA
    // ========================================================

    const forecastDates =
        forecast.time || [];

    const maxTemperatures =
        forecast.temperature_2m_max ||
        [];

    const minTemperatures =
        forecast.temperature_2m_min ||
        [];

    const forecastCodes =
        forecast.weather_code ||
        [];

    const rainProbabilities =
        forecast
            .precipitation_probability_max ||
        [];

    const forecastWind =
        forecast.wind_speed_10m_max ||
        [];


    // ========================================================
    // AGRICULTURAL INSIGHT
    // ========================================================

    const getAgriculturalInsight =
        () => {
            if (!weather) {
                return t.insightSelectLocation;
            }

            if (
                precipitation > 5
            ) {
                return t.insightRain;
            }

            if (
                humidity !==
                    undefined &&
                humidity > 80
            ) {
                return t.insightHumidity;
            }

            if (
                temperature !==
                    undefined &&
                temperature > 35
            ) {
                return t.insightHot;
            }

            if (
                temperature !==
                    undefined &&
                temperature < 15
            ) {
                return t.insightCold;
            }

            return t.insightNormal;
        };


    // ========================================================
    // RENDER
    // ========================================================

    return (
        <div
            className="weather-page"
            lang={language}
        >
            <div className="weather-container">

                {/* =================================================
                    TOP NAVIGATION
                ================================================= */}

                <div className="weather-top-navigation">

                    <button
                        type="button"
                        className="weather-back-button"
                        onClick={
                            handleBackToDashboard
                        }
                    >
                        {t.backDashboard}
                    </button>

                    <div className="weather-language-switcher">

                        <button
                            type="button"
                            className={`weather-language-button ${
                                language ===
                                "en"
                                    ? "active"
                                    : ""
                            }`}
                            onClick={() =>
                                setLanguage(
                                    "en"
                                )
                            }
                        >
                            English
                        </button>

                        <button
                            type="button"
                            className={`weather-language-button ${
                                language ===
                                "kn"
                                    ? "active"
                                    : ""
                            }`}
                            onClick={() =>
                                setLanguage(
                                    "kn"
                                )
                            }
                        >
                            ಕನ್ನಡ
                        </button>

                    </div>
                </div>


                {/* =================================================
                    HEADER
                ================================================= */}

                <div className="weather-header">

                    <div className="weather-header-icon">
                        🌦️
                    </div>

                    <div>
                        <h1>
                            {t.title}
                        </h1>

                        <p>
                            {t.subtitle}
                        </p>
                    </div>

                </div>


                {/* =================================================
                    MANUAL LOCATION
                ================================================= */}

                <div className="weather-manual-card">

                    <h2>
                        {t.enterFarmLocation}
                    </h2>

                    <p>
                        {t.enterLocationDescription}
                    </p>

                    <form
                        onSubmit={
                            handleManualWeather
                        }
                    >

                        <div className="weather-manual-grid">

                            {/* STATE */}

                            <div className="weather-field">

                                <label>
                                    {t.state}
                                </label>

                                <input
                                    type="text"
                                    value={state}
                                    onChange={(e) => {
                                        setState(
                                            e.target.value
                                        );

                                        setSelectedPlace(
                                            null
                                        );

                                        setWeather(
                                            null
                                        );
                                    }}
                                    placeholder={
                                        t.statePlaceholder
                                    }
                                />

                            </div>


                            {/* DISTRICT */}

                            <div className="weather-field">

                                <label>
                                    {t.district}
                                </label>

                                <input
                                    type="text"
                                    value={
                                        district
                                    }
                                    onChange={(e) => {
                                        setDistrict(
                                            e.target.value
                                        );

                                        setSelectedPlace(
                                            null
                                        );

                                        setWeather(
                                            null
                                        );
                                    }}
                                    placeholder={
                                        t.districtPlaceholder
                                    }
                                />

                            </div>


                            {/* VILLAGE */}

                            <div className="weather-field location-search-field">

                                <label>
                                    {
                                        t.villageTownCity
                                    }
                                </label>

                                <input
                                    type="text"
                                    value={village}
                                    onChange={(e) => {
                                        setVillage(
                                            e.target.value
                                        );

                                        setSelectedPlace(
                                            null
                                        );

                                        setWeather(
                                            null
                                        );
                                    }}
                                    placeholder={
                                        t.villagePlaceholder
                                    }
                                    autoComplete="off"
                                />


                                {searchingLocations && (
                                    <div className="location-search-status">
                                        {
                                            t.searching
                                        }
                                    </div>
                                )}


                                {locationResults.length >
                                    0 && (
                                    <div className="location-results">

                                        {locationResults.map(
                                            (
                                                place,
                                                index
                                            ) => (
                                                <button
                                                    type="button"
                                                    className="location-result"
                                                    key={`${place.latitude}-${place.longitude}-${index}`}
                                                    onClick={() =>
                                                        handlePlaceSelect(
                                                            place
                                                        )
                                                    }
                                                >

                                                    <strong>
                                                        📍{" "}
                                                        {
                                                            place.name
                                                        }
                                                    </strong>

                                                    <span>
                                                        {
                                                            place.display_name
                                                        }
                                                    </span>

                                                </button>
                                            )
                                        )}

                                    </div>
                                )}

                            </div>

                        </div>


                        {/* SELECTED PLACE */}

                        {selectedPlace && (
                            <div className="selected-place-box">

                                <strong>
                                    {
                                        t.locationSelected
                                    }
                                </strong>

                                <span>
                                    {
                                        selectedPlace.display_name
                                    }
                                </span>

                            </div>
                        )}


                        {/* WEATHER BUTTON */}

                        <button
                            type="submit"
                            className="manual-weather-button"
                            disabled={
                                loading
                            }
                        >
                            {loading
                                ? t.loading
                                : t.getWeather}
                        </button>

                    </form>

                </div>


                {/* =================================================
                    MAP
                ================================================= */}

                <div className="weather-map-card">

                    <h2>
                        {t.selectFarmMap}
                    </h2>

                    <p>
                        {t.mapDescription}
                    </p>


                    <div className="weather-map-wrapper">

                        <MapContainer
                            center={[
                                20.5937,
                                78.9629,
                            ]}
                            zoom={5}
                            scrollWheelZoom={
                                true
                            }
                            zoomControl={
                                true
                            }
                            style={{
                                width:
                                    "100%",
                                height:
                                    "100%",
                            }}
                        >

                            <TileLayer
                                attribution="&copy; OpenStreetMap contributors"
                                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            />


                            <MapCenterTracker
                                onCenterChange={
                                    setMapCenter
                                }
                            />


                            <MapViewController
                                location={
                                    selectedLocation
                                }
                            />


                            {selectedLocation && (
                                <Marker
                                    position={[
                                        selectedLocation.latitude,
                                        selectedLocation.longitude,
                                    ]}
                                    draggable={
                                        true
                                    }
                                    eventHandlers={{
                                        dragend:
                                            (
                                                event
                                            ) => {
                                                const position =
                                                    event
                                                        .target
                                                        .getLatLng();

                                                const location =
                                                    {
                                                        latitude:
                                                            position.lat,

                                                        longitude:
                                                            position.lng,
                                                    };

                                                setSelectedLocation(
                                                    location
                                                );

                                                setMapCenter(
                                                    location
                                                );
                                            },
                                    }}
                                />
                            )}

                        </MapContainer>


                        {/* CROSSHAIR */}

                        <div className="map-crosshair">
                            ✚
                        </div>


                        {/* MAP INSTRUCTION */}

                        <div className="map-instruction">
                            {
                                t.mapInstruction
                            }
                        </div>

                    </div>


                    {/* MAP CENTER */}

                    <div className="map-center-info">

                        <span>
                            {t.mapCenter}
                        </span>

                        <small>
                            {t.latitude}:{" "}
                            {mapCenter.latitude.toFixed(
                                5
                            )}

                            {" | "}

                            {t.longitude}:{" "}
                            {mapCenter.longitude.toFixed(
                                5
                            )}
                        </small>

                    </div>


                    {/* SELECT CENTER */}

                    <button
                        type="button"
                        className="weather-select-map-button"
                        onClick={
                            handleSelectMapCenter
                        }
                    >
                        {t.selectCenter}
                    </button>


                    {/* SELECTED LOCATION */}

                    {selectedLocation && (
                        <div className="weather-selected-location">

                            <div className="weather-selected-location-info">

                                <div className="weather-selected-location-icon">
                                    📍
                                </div>

                                <div className="weather-selected-location-text">

                                    <strong>
                                        {
                                            t.selectedFarmLocation
                                        }
                                    </strong>

                                    <span>
                                        {
                                            t.latitude
                                        }:{" "}
                                        {selectedLocation.latitude.toFixed(
                                            5
                                        )}

                                        {" | "}

                                        {
                                            t.longitude
                                        }:{" "}
                                        {selectedLocation.longitude.toFixed(
                                            5
                                        )}
                                    </span>

                                </div>

                            </div>


                            <button
                                type="button"
                                className="weather-location-button"
                                onClick={
                                    handleMapWeather
                                }
                                disabled={
                                    loading
                                }
                            >
                                {loading
                                    ? t.loading
                                    : t.getMapWeather}
                            </button>

                        </div>
                    )}


                    {/* USE MY LOCATION */}

                    <button
                        type="button"
                        className="weather-location-button use-location-button"
                        onClick={
                            handleUseMyLocation
                        }
                        disabled={
                            locationLoading
                        }
                    >
                        {locationLoading
                            ? t.detectingLocation
                            : t.useMyLocation}
                    </button>

                </div>


                {/* =================================================
                    ERROR
                ================================================= */}

                {error && (
                    <div className="weather-error">
                        ⚠️ {error}
                    </div>
                )}


                {/* =================================================
                    LOADING
                ================================================= */}

                {loading && (
                    <div className="weather-loading">

                        <div className="weather-spinner">
                            🌦️
                        </div>

                        <p>
                            {
                                t.loadingWeather
                            }
                        </p>

                    </div>
                )}


                {/* =================================================
                    WEATHER RESULT
                ================================================= */}

                {weather &&
                    !loading && (
                        <>

                            {/* CURRENT WEATHER */}

                            <div className="weather-card">

                                <div className="weather-main">

                                    <div className="weather-condition">
                                        {getWeatherIcon(
                                            weatherCode
                                        )}
                                    </div>


                                    <div className="weather-location">

                                        <h2>
                                            {
                                                weather
                                                    .location
                                                    ?.name ||
                                                village ||
                                                district ||
                                                state ||
                                                t.selectedLocation
                                            }
                                        </h2>

                                        <p>
                                            {getWeatherDescription(
                                                weatherCode,
                                                language
                                            )}
                                        </p>

                                        <span>
                                            📍{" "}
                                            {
                                                weather
                                                    .location
                                                    ?.display_name ||
                                                weather
                                                    .location
                                                    ?.address ||
                                                `${village}, ${district}, ${state}`
                                            }
                                        </span>

                                    </div>

                                </div>


                                {/* CURRENT VALUES */}

                                <div className="weather-values">

                                    <div className="weather-value">

                                        <span>
                                            {
                                                t.temperature
                                            }
                                        </span>

                                        <strong>
                                            {temperature !==
                                            undefined
                                                ? `${temperature}°C`
                                                : t.na}
                                        </strong>

                                    </div>


                                    <div className="weather-value">

                                        <span>
                                            {
                                                t.humidity
                                            }
                                        </span>

                                        <strong>
                                            {humidity !==
                                            undefined
                                                ? `${humidity}%`
                                                : t.na}
                                        </strong>

                                    </div>


                                    <div className="weather-value">

                                        <span>
                                            {
                                                t.rainfall
                                            }
                                        </span>

                                        <strong>
                                            {precipitation !==
                                            undefined
                                                ? `${precipitation} mm`
                                                : t.na}
                                        </strong>

                                    </div>


                                    <div className="weather-value">

                                        <span>
                                            {
                                                t.windSpeed
                                            }
                                        </span>

                                        <strong>
                                            {windSpeed !==
                                            undefined
                                                ? `${windSpeed} km/h`
                                                : t.na}
                                        </strong>

                                    </div>

                                </div>

                            </div>


                            {/* =================================================
                                7 DAY FORECAST
                            ================================================= */}

                            {forecastDates.length >
                                0 && (
                                <div className="forecast-card">

                                    <h2>
                                        {t.forecast}
                                    </h2>

                                    <div className="forecast-grid">

                                        {forecastDates
                                            .slice(
                                                0,
                                                7
                                            )
                                            .map(
                                                (
                                                    date,
                                                    index
                                                ) => {
                                                    const code =
                                                        forecastCodes[
                                                            index
                                                        ] ??
                                                        0;

                                                    return (
                                                        <div
                                                            className="forecast-item"
                                                            key={`${date}-${index}`}
                                                        >

                                                            <div className="forecast-date">
                                                                {new Date(
                                                                    `${date}T00:00:00`
                                                                ).toLocaleDateString(
                                                                    language ===
                                                                        "kn"
                                                                        ? "kn-IN"
                                                                        : "en-IN",
                                                                    {
                                                                        weekday:
                                                                            "short",

                                                                        day:
                                                                            "numeric",

                                                                        month:
                                                                            "short",
                                                                    }
                                                                )}
                                                            </div>


                                                            <div className="forecast-icon">
                                                                {getWeatherIcon(
                                                                    code
                                                                )}
                                                            </div>


                                                            <div className="forecast-description">
                                                                {getWeatherDescription(
                                                                    code,
                                                                    language
                                                                )}
                                                            </div>


                                                            <div className="forecast-temperature">

                                                                <strong>
                                                                    {maxTemperatures[
                                                                        index
                                                                    ] !==
                                                                    undefined
                                                                        ? `${Math.round(
                                                                              maxTemperatures[
                                                                                  index
                                                                              ]
                                                                          )}°`
                                                                        : "--"}
                                                                </strong>

                                                                <span>
                                                                    {minTemperatures[
                                                                        index
                                                                    ] !==
                                                                    undefined
                                                                        ? `${Math.round(
                                                                              minTemperatures[
                                                                                  index
                                                                              ]
                                                                          )}°`
                                                                        : "--"}
                                                                </span>

                                                            </div>


                                                            <div className="forecast-rain">
                                                                🌧️{" "}

                                                                {rainProbabilities[
                                                                    index
                                                                ] !==
                                                                undefined
                                                                    ? `${rainProbabilities[index]}% ${t.rain}`
                                                                    : t.na}
                                                            </div>


                                                            <div className="forecast-wind">
                                                                💨{" "}

                                                                {forecastWind[
                                                                    index
                                                                ] !==
                                                                undefined
                                                                    ? `${Math.round(
                                                                          forecastWind[
                                                                              index
                                                                          ]
                                                                      )} km/h`
                                                                    : t.na}
                                                            </div>

                                                        </div>
                                                    );
                                                }
                                            )}

                                    </div>

                                </div>
                            )}


                            {/* =================================================
                                AGRICULTURAL INSIGHT
                            ================================================= */}

                            <div className="weather-agriculture-note">

                                <h3>
                                    {
                                        t.agriculturalInsight
                                    }
                                </h3>

                                <p>
                                    {
                                        getAgriculturalInsight()
                                    }
                                </p>

                            </div>

                        </>
                    )}

            </div>
        </div>
    );
}


export default Weather;