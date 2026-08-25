import React, {
    useEffect,
    useRef,
    useState
} from "react";

import {
    useNavigate
} from "react-router-dom";

import {
    sendAssistantMessage
} from "../services/api";

import "./Assistant.css";


// =========================================================
// SUPPORTED LANGUAGES
// =========================================================

const LANGUAGES = [
    "English",
    "Kannada",
    "Hindi",
    "Telugu",
    "Tamil",
    "Malayalam",
    "Marathi"
];


// =========================================================
// SPEECH LANGUAGE CODES
// =========================================================

const SPEECH_LANGUAGES = {
    English: "en-IN",
    Kannada: "kn-IN",
    Hindi: "hi-IN",
    Telugu: "te-IN",
    Tamil: "ta-IN",
    Malayalam: "ml-IN",
    Marathi: "mr-IN"
};


// =========================================================
// PLACEHOLDERS
// =========================================================

const getPlaceholder = (language) => {

    switch (language) {

        case "Kannada":
            return "ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಯನ್ನು ಇಲ್ಲಿ ಬರೆಯಿರಿ...";

        case "Hindi":
            return "अपना कृषि प्रश्न यहाँ लिखें...";

        case "Telugu":
            return "మీ వ్యవసాయ ప్రశ్నను ఇక్కడ టైప్ చేయండి...";

        case "Tamil":
            return "உங்கள் விவசாய கேள்வியை இங்கே எழுதுங்கள்...";

        case "Malayalam":
            return "നിങ്ങളുടെ കാർഷിക ചോദ്യം ഇവിടെ എഴുതുക...";

        case "Marathi":
            return "तुमचा कृषी प्रश्न येथे लिहा...";

        default:
            return "Ask your agriculture question...";
    }
};


// =========================================================
// WELCOME MESSAGE
// =========================================================

const getWelcomeMessage = (language) => {

    switch (language) {

        case "Kannada":
            return "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ AI ಕೃಷಿ ಸಹಾಯಕ. ಬೆಳೆ, ಮಣ್ಣು, ಗೊಬ್ಬರ, ನೀರಾವರಿ ಮತ್ತು ಹವಾಮಾನದ ಬಗ್ಗೆ ನಿಮ್ಮ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಬಹುದು.";

        case "Hindi":
            return "नमस्ते! मैं आपका AI कृषि सहायक हूँ। आप फसल, मिट्टी, उर्वरक, सिंचाई और मौसम के बारे में प्रश्न पूछ सकते हैं।";

        case "Telugu":
            return "నమస్కారం! నేను మీ AI వ్యవసాయ సహాయకుడిని. పంటలు, నేల, ఎరువులు, నీటిపారుదల మరియు వాతావరణం గురించి ప్రశ్నలు అడగవచ్చు.";

        case "Tamil":
            return "வணக்கம்! நான் உங்கள் AI விவசாய உதவியாளர். பயிர்கள், மண், உரம், பாசனம் மற்றும் வானிலை பற்றி கேள்விகள் கேட்கலாம்.";

        case "Malayalam":
            return "നമസ്കാരം! ഞാൻ നിങ്ങളുടെ AI കാർഷിക സഹായി. വിളകൾ, മണ്ണ്, വളം, ജലസേചനം, കാലാവസ്ഥ എന്നിവയെക്കുറിച്ച് ചോദ്യങ്ങൾ ചോദിക്കാം.";

        case "Marathi":
            return "नमस्कार! मी तुमचा AI कृषी सहाय्यक आहे. पिके, माती, खत, सिंचन आणि हवामानाबद्दल प्रश्न विचारू शकता.";

        default:
            return "Hello! I am your AI Agriculture Assistant. You can ask me about crops, soil, fertilizer, irrigation, weather and farming.";
    }
};


// =========================================================
// FORMAT AI RESPONSE
// =========================================================

const formatResponse = (text) => {

    if (!text) {
        return "";
    }

    return String(text)
        .replace(/\r\n/g, "\n")
        .replace(/\r/g, "\n")
        .trim();
};


// =========================================================
// ASSISTANT COMPONENT
// =========================================================

function Assistant() {

    // =====================================================
    // NAVIGATION
    // =====================================================

    const navigate = useNavigate();


    // =====================================================
    // CHAT STATE
    // =====================================================

    const [messages, setMessages] = useState([
        {
            role: "assistant",
            content: getWelcomeMessage("English")
        }
    ]);

    const [input, setInput] = useState("");

    const [language, setLanguage] =
        useState("English");

    const [loading, setLoading] =
        useState(false);


    // =====================================================
    // VOICE STATE
    // =====================================================

    const [isListening, setIsListening] =
        useState(false);

    const [voiceSupported, setVoiceSupported] =
        useState(true);

    const [speechEnabled, setSpeechEnabled] =
        useState(true);


    // =====================================================
    // REFS
    // =====================================================

    const messagesEndRef =
        useRef(null);

    const recognitionRef =
        useRef(null);


    // =====================================================
    // BACK TO DASHBOARD
    // =====================================================

    const handleBackToDashboard = () => {

        stopSpeaking();

        if (isListening) {

            try {
                recognitionRef.current?.stop();
            }

            catch (error) {
                console.log(error);
            }
        }

        navigate("/dashboard");
    };


    // =====================================================
    // INITIALIZE SPEECH RECOGNITION
    // =====================================================

    useEffect(() => {

        const SpeechRecognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;


        if (!SpeechRecognition) {

            setVoiceSupported(false);

            recognitionRef.current = null;

            return;
        }


        const recognition =
            new SpeechRecognition();


        recognition.continuous = false;

        recognition.interimResults = true;

        recognition.maxAlternatives = 1;

        recognition.lang =
            SPEECH_LANGUAGES[language] ||
            "en-IN";


        // -------------------------------------------------
        // START
        // -------------------------------------------------

        recognition.onstart = () => {

            setIsListening(true);

        };


        // -------------------------------------------------
        // RESULT
        // -------------------------------------------------

        recognition.onresult = (event) => {

            let transcript = "";


            for (
                let i = event.resultIndex;
                i < event.results.length;
                i++
            ) {

                transcript +=
                    event.results[i][0].transcript;
            }


            setInput(transcript);

        };


        // -------------------------------------------------
        // ERROR
        // -------------------------------------------------

        recognition.onerror = (event) => {

            console.error(
                "Speech recognition error:",
                event.error
            );


            setIsListening(false);


            if (event.error === "not-allowed") {

                alert(
                    "Microphone permission was denied. Please allow microphone access in your browser."
                );

            }

        };


        // -------------------------------------------------
        // END
        // -------------------------------------------------

        recognition.onend = () => {

            setIsListening(false);

        };


        recognitionRef.current =
            recognition;


        // -------------------------------------------------
        // CLEANUP
        // -------------------------------------------------

        return () => {

            try {

                recognition.stop();

            }

            catch (error) {

                console.log(
                    "Speech cleanup:",
                    error
                );

            }

            recognitionRef.current = null;

        };

    }, [language]);


    // =====================================================
    // AUTO SCROLL
    // =====================================================

    useEffect(() => {

        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth"
        });

    }, [messages, loading]);


    // =====================================================
    // CHANGE LANGUAGE
    // =====================================================

    const handleLanguageChange = (event) => {

        const selectedLanguage =
            event.target.value;


        if (isListening) {

            try {

                recognitionRef.current?.stop();

            }

            catch (error) {

                console.log(error);

            }

        }


        stopSpeaking();


        setLanguage(
            selectedLanguage
        );


        setMessages((previous) => {

            if (previous.length === 1) {

                return [
                    {
                        role: "assistant",
                        content:
                            getWelcomeMessage(
                                selectedLanguage
                            )
                    }
                ];

            }

            return previous;

        });

    };


    // =====================================================
    // START / STOP VOICE INPUT
    // =====================================================

    const toggleVoiceInput = () => {

        if (!voiceSupported) {

            alert(
                "Voice input is not supported in this browser. Please use Google Chrome or Microsoft Edge."
            );

            return;
        }


        const recognition =
            recognitionRef.current;


        if (!recognition) {
            return;
        }


        // -------------------------------------------------
        // STOP
        // -------------------------------------------------

        if (isListening) {

            try {

                recognition.stop();

            }

            catch (error) {

                console.error(
                    "Unable to stop speech recognition:",
                    error
                );

            }

            return;
        }


        // -------------------------------------------------
        // START
        // -------------------------------------------------

        try {

            stopSpeaking();


            recognition.lang =
                SPEECH_LANGUAGES[language] ||
                "en-IN";


            setInput("");


            recognition.start();

        }

        catch (error) {

            console.error(
                "Unable to start voice recognition:",
                error
            );

        }

    };


    // =====================================================
    // TEXT TO SPEECH
    // =====================================================

    const speakResponse = (text) => {

        if (
            !speechEnabled ||
            !window.speechSynthesis ||
            !text
        ) {

            return;
        }


        stopSpeaking();


        const utterance =
            new SpeechSynthesisUtterance(text);


        utterance.lang =
            SPEECH_LANGUAGES[language] ||
            "en-IN";


        utterance.rate = 0.95;

        utterance.pitch = 1;

        utterance.volume = 1;


        window.speechSynthesis.speak(
            utterance
        );

    };


    // =====================================================
    // STOP SPEAKING
    // =====================================================

    const stopSpeaking = () => {

        if (
            typeof window !== "undefined" &&
            window.speechSynthesis
        ) {

            window.speechSynthesis.cancel();

        }

    };


    // =====================================================
    // SEND MESSAGE
    // =====================================================

    const handleSend = async () => {

        const message =
            input.trim();


        if (
            !message ||
            loading
        ) {

            return;
        }


        // -------------------------------------------------
        // STOP LISTENING
        // -------------------------------------------------

        if (isListening) {

            try {

                recognitionRef.current?.stop();

            }

            catch (error) {

                console.log(error);

            }

        }


        stopSpeaking();


        // -------------------------------------------------
        // ADD USER MESSAGE
        // -------------------------------------------------

        setMessages((previous) => [

            ...previous,

            {
                role: "user",
                content: message
            }

        ]);


        setInput("");

        setLoading(true);


        try {

            console.log(
                "Sending assistant request:",
                {
                    message,
                    language
                }
            );


            const result =
                await sendAssistantMessage(
                    message,
                    language
                );


            console.log(
                "Assistant API response:",
                result
            );


            const responseText =
                formatResponse(
                    result?.response
                );


            const finalResponse =
                responseText ||
                (
                    language === "Kannada"
                        ? "ಕ್ಷಮಿಸಿ, ಯಾವುದೇ ಉತ್ತರವನ್ನು ಪಡೆಯಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ."
                        : language === "Hindi"
                            ? "क्षमा करें, मुझे कोई उत्तर नहीं मिला।"
                            : language === "Telugu"
                                ? "క్షమించండి, సమాధానం పొందలేకపోయాను."
                                : language === "Tamil"
                                    ? "மன்னிக்கவும், பதிலைப் பெற முடியவில்லை."
                                    : language === "Malayalam"
                                        ? "ക്ഷമിക്കണം, മറുപടി ലഭിച്ചില്ല."
                                        : language === "Marathi"
                                            ? "क्षमस्व, मला उत्तर मिळाले नाही."
                                            : "Sorry, I could not generate a response."
                );


            // -------------------------------------------------
            // ADD AI RESPONSE
            // -------------------------------------------------

            setMessages((previous) => [

                ...previous,

                {
                    role: "assistant",
                    content: finalResponse
                }

            ]);


            // -------------------------------------------------
            // VOICE REPLY
            // -------------------------------------------------

            speakResponse(
                finalResponse
            );

        }

        catch (error) {

            console.error(
                "Assistant error:",
                error
            );


            let errorMessage =
                "Sorry, I could not connect to the AI Agriculture Assistant.";


            if (
                error?.response?.data?.detail
            ) {

                const detail =
                    error.response.data.detail;


                if (
                    typeof detail === "string"
                ) {

                    errorMessage = detail;

                }

                else if (
                    typeof detail === "object"
                ) {

                    errorMessage =
                        detail.message ||
                        JSON.stringify(detail);

                }

            }

            else if (
                error?.message === "Network Error"
            ) {

                errorMessage =
                    "Cannot connect to the backend. Please make sure the FastAPI backend is running.";

            }


            setMessages((previous) => [

                ...previous,

                {
                    role: "assistant",
                    content: errorMessage,
                    error: true
                }

            ]);

        }

        finally {

            setLoading(false);

        }

    };


    // =====================================================
    // ENTER KEY
    // =====================================================

    const handleKeyDown = (event) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            handleSend();

        }

    };


    // =====================================================
    // CLEAR CHAT
    // =====================================================

    const clearChat = () => {

        stopSpeaking();


        if (isListening) {

            try {

                recognitionRef.current?.stop();

            }

            catch (error) {

                console.log(error);

            }

        }


        setMessages([
            {
                role: "assistant",
                content:
                    getWelcomeMessage(
                        language
                    )
            }
        ]);


        setInput("");

    };


    // =====================================================
    // RENDER
    // =====================================================

    return (

        <div className="assistant-page">


            {/* =================================================
                TOP NAVIGATION
            ================================================= */}

            <div className="assistant-topbar">

                <button
                    type="button"
                    className="back-dashboard-button"
                    onClick={
                        handleBackToDashboard
                    }
                >

                    <span className="back-icon">
                        ←
                    </span>

                    <span>
                        Back to Dashboard
                    </span>

                </button>


                <div className="assistant-online-status">

                    <span className="online-dot"></span>

                    AI Assistant Online

                </div>

            </div>


            {/* =================================================
                HEADER
            ================================================= */}

            <div className="assistant-header">

                <div className="assistant-title-area">

                    <div className="assistant-logo">

                        🌱

                    </div>


                    <div>

                        <div className="assistant-title-row">

                            <h1>
                                AI Agriculture Assistant
                            </h1>

                            <span className="assistant-badge">
                                AI
                            </span>

                        </div>


                        <p>
                            Your smart farming companion for
                            crops, soil, fertilizer, irrigation,
                            weather and farming guidance.
                        </p>

                    </div>

                </div>


                <button
                    type="button"
                    className="clear-chat-button"
                    onClick={clearChat}
                    disabled={loading}
                >

                    🗑 Clear Chat

                </button>

            </div>


            {/* =================================================
                LANGUAGE
            ================================================= */}

            <div className="assistant-language">

                <div className="language-left">

                    <span className="language-icon">
                        🌐
                    </span>


                    <label
                        htmlFor="assistant-language"
                    >
                        Response Language
                    </label>

                </div>


                <select
                    id="assistant-language"
                    value={language}
                    onChange={
                        handleLanguageChange
                    }
                    disabled={loading}
                >

                    {LANGUAGES.map(
                        (item) => (

                            <option
                                key={item}
                                value={item}
                            >
                                {item}
                            </option>

                        )
                    )}

                </select>


                <span
                    className={
                        voiceSupported
                            ? "voice-status available"
                            : "voice-status unavailable"
                    }
                >

                    {voiceSupported
                        ? "🎤 Voice available"
                        : "🎤 Voice unavailable"}

                </span>

            </div>


            {/* =================================================
                CHAT
            ================================================= */}

            <div className="assistant-chat">

                {messages.map(
                    (
                        message,
                        index
                    ) => (

                        <div
                            key={index}
                            className={
                                `assistant-message ${
                                    message.role === "user"
                                        ? "user-message"
                                        : "ai-message"
                                }`
                            }
                        >

                            <div className="message-label">

                                <span>

                                    {
                                        message.role === "user"
                                            ? "You"
                                            : "🌱 AI Assistant"
                                    }

                                </span>

                            </div>


                            <div
                                className={
                                    `message-content ${
                                        message.error
                                            ? "message-error"
                                            : ""
                                    }`
                                }
                            >

                                {message.content}

                            </div>

                        </div>

                    )
                )}


                {/* =================================================
                    LOADING
                ================================================= */}

                {loading && (

                    <div className="assistant-message ai-message">

                        <div className="message-label">

                            🌱 AI Assistant

                        </div>


                        <div className="typing-indicator">

                            <span></span>

                            <span></span>

                            <span></span>

                            <span className="thinking-text">
                                Thinking...
                            </span>

                        </div>

                    </div>

                )}


                <div
                    ref={messagesEndRef}
                />

            </div>


            {/* =================================================
                VOICE CONTROLS
            ================================================= */}

            <div className="assistant-voice-controls">

                <button
                    type="button"
                    className={
                        isListening
                            ? "voice-button listening"
                            : "voice-button"
                    }
                    onClick={
                        toggleVoiceInput
                    }
                    disabled={
                        loading ||
                        !voiceSupported
                    }
                >

                    <span className="voice-button-icon">

                        {isListening
                            ? "⏹"
                            : "🎤"}

                    </span>


                    <span>

                        {isListening
                            ? "Stop Listening"
                            : "Speak Question"}

                    </span>

                </button>


                <button
                    type="button"
                    className={
                        speechEnabled
                            ? "speech-button active"
                            : "speech-button"
                    }
                    onClick={() =>
                        setSpeechEnabled(
                            (previous) =>
                                !previous
                        )
                    }
                >

                    {speechEnabled
                        ? "🔊 Voice Reply On"
                        : "🔇 Voice Reply Off"}

                </button>


                <button
                    type="button"
                    className="stop-speaking-button"
                    onClick={stopSpeaking}
                >

                    ⏹ Stop Voice

                </button>

            </div>


            {/* =================================================
                INPUT
            ================================================= */}

            <div className="assistant-input-area">

                <textarea
                    value={input}
                    onChange={
                        (event) =>
                            setInput(
                                event.target.value
                            )
                    }
                    onKeyDown={
                        handleKeyDown
                    }
                    placeholder={
                        getPlaceholder(
                            language
                        )
                    }
                    rows={2}
                    maxLength={2000}
                    disabled={loading}
                />


                <button
                    type="button"
                    className="send-button"
                    onClick={handleSend}
                    disabled={
                        loading ||
                        !input.trim()
                    }
                >

                    {loading
                        ? "..."
                        : "Send ➤"}

                </button>

            </div>


            {/* =================================================
                FOOTER
            ================================================= */}

            <div className="assistant-footer">

                <span>
                    🌱 AI-powered agriculture guidance
                </span>

                <span className="footer-separator">
                    •
                </span>

                <span>
                    Voice input and voice replies
                    are supported in compatible browsers.
                </span>

                <span className="footer-separator">
                    •
                </span>

                <span>
                    Verify important farming decisions
                    with a qualified agricultural professional.
                </span>

            </div>

        </div>

    );

}


export default Assistant;

