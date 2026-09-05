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

            config.headers =
                config.headers || {};

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

            config.headers =
                config.headers || {};

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

        }

        else if (error.request) {

            console.error(
                "API Server did not respond:",
                error.message
            );

        }

        else {

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

        if (
            error.code ===
            "ECONNABORTED"
        ) {

            console.error(
                "AI Assistant timeout:",
                error.message
            );

        }

        else if (error.response) {

            console.error(
                "AI Assistant API Error:",
                error.response.status,
                error.response.data
            );

        }

        else if (error.request) {

            console.error(
                "AI Assistant server did not respond:",
                error.message
            );

        }

        else {

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
        await API.get(
            "/iot/latest"
        );

    return response.data;

};


// =========================================================
// CROP
// =========================================================

export const getCropRecommendation = async (
    data
) => {

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

export const getSoilAnalysis = async (
    data
) => {

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
//
// Current fertilizer model uses:
//
// 1. Nitrogen
// 2. Phosphorus
// 3. Potassium
// 4. pH
// 5. Moisture
// 6. Temperature
//
// Backend additionally requires:
//
// 7. crop_type
//
// Backend endpoint:
// POST /fertilizer/recommend
//
// =========================================================

export const getFertilizerRecommendation = async (
    data
) => {

    // -----------------------------------------------------
    // Validate input
    // -----------------------------------------------------

    if (!data) {

        throw new Error(
            "Fertilizer input data is required."
        );

    }


    // -----------------------------------------------------
    // Prepare fertilizer request
    // -----------------------------------------------------

    const fertilizerData = {

        nitrogen:
            Number(data.nitrogen),

        phosphorus:
            Number(data.phosphorus),

        potassium:
            Number(data.potassium),

        ph:
            Number(data.ph),

        moisture:
            Number(data.moisture),

        temperature:
            Number(data.temperature),

        // IMPORTANT:
        // Backend requires crop_type
        crop_type:
            String(
                data.crop_type || ""
            )
                .trim()
                .toLowerCase(),

    };


    // -----------------------------------------------------
    // Validate numeric values
    // -----------------------------------------------------

    const numericFields = {

        nitrogen:
            fertilizerData.nitrogen,

        phosphorus:
            fertilizerData.phosphorus,

        potassium:
            fertilizerData.potassium,

        ph:
            fertilizerData.ph,

        moisture:
            fertilizerData.moisture,

        temperature:
            fertilizerData.temperature,

    };


    const invalidFields =
        Object.entries(
            numericFields
        )

            .filter(
                ([, value]) =>
                    !Number.isFinite(value)
            )

            .map(
                ([key]) =>
                    key
            );


    if (
        invalidFields.length > 0
    ) {

        throw new Error(
            `Invalid fertilizer sensor values: ${invalidFields.join(", ")}`
        );

    }


    // -----------------------------------------------------
    // Validate crop type
    // -----------------------------------------------------

    if (
        !fertilizerData.crop_type
    ) {

        throw new Error(
            "Crop type is required for fertilizer recommendation."
        );

    }


    // -----------------------------------------------------
    // Console debugging
    // -----------------------------------------------------

    console.log(
        "Fertilizer API request:",
        fertilizerData
    );


    // -----------------------------------------------------
    // API REQUEST
    // -----------------------------------------------------

    const response =
        await API.post(

            "/fertilizer/recommend",

            fertilizerData

        );


    // -----------------------------------------------------
    // Console response
    // -----------------------------------------------------

    console.log(
        "Fertilizer API response:",
        response.data
    );


    return response.data;

};


// =========================================================
// IRRIGATION
// =========================================================

export const getIrrigationPrediction = async (
    data
) => {

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

export const getCurrentWeather = async (
    location
) => {

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

export const searchWeatherLocations = async (

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

export const getWeatherStatus = async () => {

    const response =
        await API.get(
            "/weather/"
        );

    return response.data;

};


// =========================================================
// WEATHER FORECAST
// =========================================================

export const getWeatherForecast = async (
    location
) => {

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

    if (
        notificationId ===
        null ||
        notificationId ===
        undefined
    ) {

        throw new Error(
            "Notification ID is required."
        );

    }


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
// AI ASSISTANT - CHAT
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

            message:
                cleanMessage,

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

                    message:
                        cleanMessage,

                    language,

                }

            );


        console.log(
            "AI Assistant response:",
            response.data
        );


        return response.data;

    }

    catch (error) {

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

export const generateAssistantSpeech = async (

    text,
    language = "English"

) => {

    if (
        !text ||
        !text.trim()
    ) {

        throw new Error(
            "Text for speech cannot be empty."
        );

    }


    const cleanText =
        text.trim();


    console.log(
        "AI Assistant TTS request:",
        {

            text:
                cleanText,

            language,

            endpoint:
                `${API_BASE_URL}/tts/speak`,

        }
    );


    try {

        const response =
            await ASSISTANT_API.post(

                "/tts/speak",

                {

                    text:
                        cleanText,

                    language,

                },

                {

                    responseType:
                        "blob",

                    headers: {

                        Accept:
                            "audio/mpeg",

                    },

                }

            );


        console.log(

            "AI Assistant TTS audio received:",

            {

                type:
                    response.data?.type,

                size:
                    response.data?.size,

            }

        );


        return response.data;

    }

    catch (error) {

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