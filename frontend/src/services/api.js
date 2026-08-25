import axios from "axios";


// =========================================================
// API BASE URL
// =========================================================

const API_BASE_URL =
    import.meta.env.VITE_API_URL ||
    "https://ai-smart-agriculture-jf61.onrender.com";

// =========================================================
// NORMAL AXIOS INSTANCE
// =========================================================
// Used by Crop, Soil, Fertilizer, Irrigation, Weather,
// IoT and Notification modules.
// =========================================================

const API = axios.create({
    baseURL: API_BASE_URL,

    headers: {
        "Content-Type": "application/json",
    },

    timeout: 15000,
});


// =========================================================
// AI ASSISTANT AXIOS INSTANCE
// =========================================================
// Assistant responses can take longer because the backend
// may need to process AI/model requests.
// =========================================================

const ASSISTANT_API = axios.create({
    baseURL: API_BASE_URL,

    headers: {
        "Content-Type": "application/json",
    },

    timeout: 60000,
});


// =========================================================
// JWT TOKEN INTERCEPTOR - NORMAL API
// =========================================================

API.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token");

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
// JWT TOKEN INTERCEPTOR - AI ASSISTANT
// =========================================================

ASSISTANT_API.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token");

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
// NORMAL API RESPONSE ERROR HANDLER
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
                "Server did not respond:",
                error.message
            );
        } else {
            console.error(
                "Request Error:",
                error.message
            );
        }

        return Promise.reject(error);
    }
);


// =========================================================
// AI ASSISTANT RESPONSE ERROR HANDLER
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
        method: method,
        url: endpoint,
        data: data,
    });

    return response.data;
};


// =========================================================
// IOT
// =========================================================

export const getLatestSensorData =
    async () => {

        const response =
            await API.get(
                "/iot/latest"
            );

        return response.data;
    };


// =========================================================
// CROP
// =========================================================

export const getCropRecommendation =
    async (data) => {

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

export const getSoilAnalysis =
    async (data) => {

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

export const getFertilizerRecommendation =
    async (data) => {

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

export const getIrrigationPrediction =
    async (data) => {

        try {

            console.log(
                "================================="
            );

            console.log(
                "IRRIGATION REQUEST"
            );

            console.log(
                data
            );

            console.log(
                "================================="
            );

            const response =
                await API.post(
                    "/irrigation/predict",
                    data
                );

            console.log(
                "IRRIGATION RESPONSE:",
                response.data
            );

            return response.data;

        } catch (error) {

            console.error(
                "================================="
            );

            console.error(
                "IRRIGATION API ERROR"
            );

            console.error(
                error?.response?.status
            );

            console.error(
                error?.response?.data
            );

            console.error(
                error?.message
            );

            console.error(
                "================================="
            );

            throw error;
        }
    };


// =========================================================
// WEATHER - LOCATION
// =========================================================

export const getCurrentWeather =
    async (location) => {

        if (
            !location ||
            !location.trim()
        ) {

            throw new Error(
                "Location is required."
            );
        }

        const response =
            await API.post(
                "/weather/current",
                {
                    location:
                        location.trim(),
                }
            );

        return response.data;
    };


// =========================================================
// WEATHER - COORDINATES
// =========================================================
// Used by Irrigation and Weather modules
// when browser GPS coordinates are available.
// =========================================================

export const getWeatherByCoordinates =
    async (
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
                    latitude:
                        Number(latitude),

                    longitude:
                        Number(longitude),
                }
            );

        return response.data;
    };


// =========================================================
// WEATHER SEARCH
// =========================================================

export const searchWeatherLocations =
    async (
        village,
        district = "",
        state = ""
    ) => {

        if (
            !village ||
            !village.trim()
        ) {

            throw new Error(
                "Village/location is required."
            );
        }

        const response =
            await API.get(
                "/weather/search",
                {
                    params: {

                        village:
                            village.trim(),

                        district:
                            district.trim(),

                        state:
                            state.trim(),
                    },
                }
            );

        return response.data;
    };


// =========================================================
// WEATHER STATUS
// =========================================================

export const getWeatherStatus =
    async () => {

        const response =
            await API.get(
                "/weather/"
            );

        return response.data;
    };


// =========================================================
// WEATHER FORECAST
// =========================================================

export const getWeatherForecast =
    async (location) => {

        if (
            !location ||
            !location.trim()
        ) {

            throw new Error(
                "Location is required."
            );
        }

        const response =
            await API.post(
                "/weather/forecast",
                {
                    location:
                        location.trim(),
                }
            );

        return response.data;
    };


// =========================================================
// NOTIFICATIONS
// =========================================================

export const getNotifications =
    async () => {

        const response =
            await API.get(
                "/notifications/"
            );

        return response.data;
    };


// =========================================================
// UNREAD NOTIFICATIONS
// =========================================================

export const getUnreadNotifications =
    async () => {

        const response =
            await API.get(
                "/notifications/unread"
            );

        return response.data;
    };


// =========================================================
// MARK NOTIFICATION READ
// =========================================================

export const markNotificationAsRead =
    async (
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

export const markAllNotificationsAsRead =
    async () => {

        const response =
            await API.put(
                "/notifications/read-all"
            );

        return response.data;
    };


// =========================================================
// AI ASSISTANT
// =========================================================
// Uses ASSISTANT_API instead of the normal API instance.
// Timeout = 60 seconds.
// =========================================================

export const sendAssistantMessage =
    async (
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

        console.log(
            "================================="
        );

        console.log(
            "ASSISTANT REQUEST"
        );

        console.log(
            "Message:",
            message.trim()
        );

        console.log(
            "Language:",
            language
        );

        console.log(
            "================================="
        );

        try {

            const response =
                await ASSISTANT_API.post(
                    "/assistant/chat",
                    {
                        message:
                            message.trim(),

                        language:
                            language,
                    }
                );

            console.log(
                "================================="
            );

            console.log(
                "ASSISTANT RESPONSE"
            );

            console.log(
                response.data
            );

            console.log(
                "================================="
            );

            return response.data;

        } catch (error) {

            console.error(
                "================================="
            );

            console.error(
                "ASSISTANT API ERROR"
            );

            console.error(
                "Status:",
                error?.response?.status
            );

            console.error(
                "Response:",
                error?.response?.data
            );

            console.error(
                "Code:",
                error?.code
            );

            console.error(
                "Message:",
                error?.message
            );

            console.error(
                "================================="
            );

            throw error;
        }
    };


// =========================================================
// DEFAULT EXPORT
// =========================================================

export default API;