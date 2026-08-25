import axios from "axios";


// =========================================================
// API BASE URL
// =========================================================

const API_BASE_URL =
    import.meta.env.VITE_API_URL ||
    "https://ai-smart-agriculture-jf61.onrender.com";


// =========================================================
// NORMAL API INSTANCE
// =========================================================

const API = axios.create({
    baseURL: API_BASE_URL,

    headers: {
        "Content-Type": "application/json",
    },

    timeout: 30000,
});


// =========================================================
// AI ASSISTANT API INSTANCE
// =========================================================

const ASSISTANT_API = axios.create({
    baseURL: API_BASE_URL,

    headers: {
        "Content-Type": "application/json",
    },

    timeout: 60000,
});


// =========================================================
// GET JWT TOKEN
// =========================================================

const getToken = () => {
    return localStorage.getItem("token");
};


// =========================================================
// ADD JWT TO NORMAL API REQUESTS
// =========================================================

API.interceptors.request.use(
    (config) => {

        const token = getToken();

        if (token) {

            config.headers = config.headers || {};

            config.headers.Authorization =
                `Bearer ${token}`;
        }

        return config;
    },

    (error) => {
        return Promise.reject(error);
    }
);


// =========================================================
// ADD JWT TO ASSISTANT REQUESTS
// =========================================================

ASSISTANT_API.interceptors.request.use(
    (config) => {

        const token = getToken();

        if (token) {

            config.headers = config.headers || {};

            config.headers.Authorization =
                `Bearer ${token}`;
        }

        return config;
    },

    (error) => {
        return Promise.reject(error);
    }
);


// =========================================================
// NORMAL API RESPONSE INTERCEPTOR
// =========================================================

API.interceptors.response.use(

    (response) => {
        return response;
    },

    (error) => {

        if (error.response) {

            console.error(
                "API Error:",
                error.response.status,
                error.response.data
            );

        } else if (error.request) {

            console.error(
                "API Server did not respond:",
                error.message
            );

        } else {

            console.error(
                "API Request Error:",
                error.message
            );
        }

        return Promise.reject(error);
    }
);


// =========================================================
// ASSISTANT RESPONSE INTERCEPTOR
// =========================================================

ASSISTANT_API.interceptors.response.use(

    (response) => {
        return response;
    },

    (error) => {

        if (error.code === "ECONNABORTED") {

            console.error(
                "AI Assistant timeout:",
                error.message
            );

        } else if (error.response) {

            console.error(
                "AI Assistant API Error:",
                error.response.status,
                error.response.data
            );

        } else if (error.request) {

            console.error(
                "AI Assistant server did not respond:",
                error.message
            );

        } else {

            console.error(
                "AI Assistant request error:",
                error.message
            );
        }

        return Promise.reject(error);
    }
);


// =========================================================
// GENERIC API REQUEST
// =========================================================

export const apiRequest = async (
    method,
    endpoint,
    data = null
) => {

    const response = await API({
        method,
        url: endpoint,
        data,
    });

    return response.data;
};


// =========================================================
// IOT
// =========================================================

export const getLatestSensorData = async () => {

    const response =
        await API.get("/iot/latest");

    return response.data;
};


// =========================================================
// CROP
// =========================================================

export const getCropRecommendation = async (data) => {

    const response =
        await API.post(
            "/crop/recommend",
            data
        );

    return response.data;
};


// =========================================================
// SOIL
// =========================================================

export const getSoilAnalysis = async (data) => {

    const response =
        await API.post(
            "/soil/analyze",
            data
        );

    return response.data;
};


// =========================================================
// FERTILIZER
// =========================================================

export const getFertilizerRecommendation = async (data) => {

    const response =
        await API.post(
            "/fertilizer/recommend",
            data
        );

    return response.data;
};


// =========================================================
// IRRIGATION
// =========================================================

export const getIrrigationPrediction = async (data) => {

    const response =
        await API.post(
            "/irrigation/predict",
            data
        );

    return response.data;
};


// =========================================================
// WEATHER - CURRENT
// =========================================================

export const getCurrentWeather = async (location) => {

    if (!location || !location.trim()) {

        throw new Error(
            "Location is required."
        );
    }

    const response =
        await API.post(
            "/weather/current",
            {
                location: location.trim(),
            }
        );

    return response.data;
};


// =========================================================
// WEATHER - COORDINATES
// =========================================================

export const getWeatherByCoordinates = async (
    latitude,
    longitude
) => {

    if (
        latitude === null ||
        latitude === undefined ||
        longitude === null ||
        longitude === undefined
    ) {

        throw new Error(
            "Latitude and longitude are required."
        );
    }

    const response =
        await API.post(
            "/weather/current-by-coordinates",
            {
                latitude: Number(latitude),
                longitude: Number(longitude),
            }
        );

    return response.data;
};


// =========================================================
// WEATHER SEARCH
// =========================================================

export const searchWeatherLocations = async (
    village,
    district = "",
    state = ""
) => {

    if (!village || !village.trim()) {

        throw new Error(
            "Village/location is required."
        );
    }

    const response =
        await API.get(
            "/weather/search",
            {
                params: {
                    village: village.trim(),
                    district: district.trim(),
                    state: state.trim(),
                },
            }
        );

    return response.data;
};


// =========================================================
// WEATHER STATUS
// =========================================================

export const getWeatherStatus = async () => {

    const response =
        await API.get("/weather/");

    return response.data;
};


// =========================================================
// WEATHER FORECAST
// =========================================================

export const getWeatherForecast = async (location) => {

    if (!location || !location.trim()) {

        throw new Error(
            "Location is required."
        );
    }

    const response =
        await API.post(
            "/weather/forecast",
            {
                location: location.trim(),
            }
        );

    return response.data;
};


// =========================================================
// NOTIFICATIONS
// =========================================================

export const getNotifications = async () => {

    const response =
        await API.get(
            "/notifications/"
        );

    return response.data;
};


// =========================================================
// UNREAD NOTIFICATIONS
// =========================================================

export const getUnreadNotifications = async () => {

    const response =
        await API.get(
            "/notifications/unread"
        );

    return response.data;
};


// =========================================================
// MARK NOTIFICATION READ
// =========================================================

export const markNotificationAsRead = async (
    notificationId
) => {

    const response =
        await API.put(
            `/notifications/${notificationId}/read`
        );

    return response.data;
};


// =========================================================
// MARK ALL NOTIFICATIONS READ
// =========================================================

export const markAllNotificationsAsRead = async () => {

    const response =
        await API.put(
            "/notifications/read-all"
        );

    return response.data;
};


// =========================================================
// AI ASSISTANT
// =========================================================

export const sendAssistantMessage = async (
    message,
    language = "English"
) => {

    if (
        !message ||
        !message.trim()
    ) {

        throw new Error(
            "Assistant message cannot be empty."
        );
    }

    const cleanMessage =
        message.trim();

    console.log(
        "AI Assistant request:",
        {
            message: cleanMessage,
            language,
            endpoint:
                `${API_BASE_URL}/assistant/chat`,
        }
    );

    try {

        const response =
            await ASSISTANT_API.post(
                "/assistant/chat",
                {
                    message: cleanMessage,
                    language,
                }
            );

        console.log(
            "AI Assistant response:",
            response.data
        );

        return response.data;

    } catch (error) {

        console.error(
            "AI Assistant request failed:",
            {
                status:
                    error?.response?.status,

                data:
                    error?.response?.data,

                message:
                    error?.message,

                code:
                    error?.code,
            }
        );

        throw error;
    }
};


// =========================================================
// AI ASSISTANT - TEXT TO SPEECH
// =========================================================

export const speakAssistantResponse = async (
    text,
    language = "English"
) => {

    if (
        !text ||
        !text.trim()
    ) {

        throw new Error(
            "TTS text cannot be empty."
        );
    }

    console.log(
        "AI Assistant TTS request:",
        {
            language,
            text: text.trim(),
            endpoint:
                `${API_BASE_URL}/tts/speak`,
        }
    );

    try {

        const response =
            await ASSISTANT_API.post(
                "/tts/speak",
                {
                    text: text.trim(),
                    language,
                },
                {
                    responseType: "blob",
                }
            );

        console.log(
            "AI Assistant TTS response received."
        );

        return response.data;

    } catch (error) {

        console.error(
            "AI Assistant TTS request failed:",
            {
                status:
                    error?.response?.status,

                data:
                    error?.response?.data,

                message:
                    error?.message,

                code:
                    error?.code,
            }
        );

        throw error;
    }
};


// =========================================================
// DEFAULT EXPORT
// =========================================================

export default API;