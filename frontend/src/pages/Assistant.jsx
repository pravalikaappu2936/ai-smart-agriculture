import React, {
    useEffect,
    useRef,
    useState
} from "react";

import {
    useNavigate
} from "react-router-dom";

import {
    sendAssistantMessage,
    generateAssistantSpeech
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
// SPEECH RECOGNITION LANGUAGES
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
// PLACEHOLDER
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
// FORMAT RESPONSE
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
// ERROR MESSAGE
// =========================================================

const getErrorMessage = (language) => {

    switch (language) {

        case "Kannada":
            return "ಕ್ಷಮಿಸಿ, AI ಸಹಾಯಕದಿಂದ ಉತ್ತರ ಪಡೆಯಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.";

        case "Hindi":
            return "क्षमा करें, AI सहायक से उत्तर प्राप्त नहीं हो सका। कृपया फिर से प्रयास करें।";

        case "Telugu":
            return "క్షమించండి, AI సహాయకుడి నుండి సమాధానం పొందలేకపోయాము. దయచేసి మళ్లీ ప్రయత్నించండి.";

        case "Tamil":
            return "மன்னிக்கவும், AI உதவியாளரிடமிருந்து பதிலைப் பெற முடியவில்லை. தயவுசெய்து மீண்டும் முயற்சிக்கவும்.";

        case "Malayalam":
            return "ക്ഷമിക്കണം, AI സഹായിയിൽ നിന്ന് മറുപടി ലഭിച്ചില്ല. ദയവായി വീണ്ടും ശ്രമിക്കുക.";

        case "Marathi":
            return "क्षमस्व, AI सहाय्याकडून उत्तर मिळू शकले नाही. कृपया पुन्हा प्रयत्न करा.";

        default:
            return "Sorry, I could not get a response from the AI Assistant. Please try again.";
    }
};


// =========================================================
// ASSISTANT COMPONENT
// =========================================================

function Assistant() {

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

    const [input, setInput] =
        useState("");

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

    // Stores backend-generated audio
    const speechAudioRef =
        useRef(null);


    // =====================================================
    // SPEECH RECOGNITION
    // =====================================================

    useEffect(() => {

        if (typeof window === "undefined") {
            return;
        }

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


        recognition.onstart = () => {

            setIsListening(true);
        };


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

            setInput(
                transcript.trim()
            );
        };


        recognition.onerror = (event) => {

            console.error(
                "Speech recognition error:",
                event.error
            );

            setIsListening(false);


            if (
                event.error === "not-allowed"
            ) {

                alert(
                    "Microphone permission was denied. Please allow microphone access in your browser."
                );
            }
        };


        recognition.onend = () => {

            setIsListening(false);
        };


        recognitionRef.current =
            recognition;


        return () => {

            try {

                recognition.stop();

            } catch (error) {

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
    // STOP VOICE
    // =====================================================

    const stopSpeaking = () => {

        // Stop backend-generated audio
        if (speechAudioRef.current) {

            try {

                speechAudioRef.current.pause();

                speechAudioRef.current.currentTime = 0;

            } catch (error) {

                console.error(
                    "Unable to stop backend audio:",
                    error
                );
            }

            speechAudioRef.current = null;
        }


        // Also stop browser speech synthesis
        if (
            typeof window !== "undefined" &&
            window.speechSynthesis
        ) {

            window.speechSynthesis.cancel();
        }
    };


    // =====================================================
    // BACK TO DASHBOARD
    // =====================================================

    const handleBackToDashboard = () => {

        stopSpeaking();


        if (isListening) {

            try {

                recognitionRef.current?.stop();

            } catch (error) {

                console.log(error);
            }
        }


        navigate("/dashboard");
    };


    // =====================================================
    // CHANGE LANGUAGE
    // =====================================================

    const handleLanguageChange = (event) => {

        const selectedLanguage =
            event.target.value;


        if (isListening) {

            try {

                recognitionRef.current?.stop();

            } catch (error) {

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
    // VOICE INPUT
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


        if (isListening) {

            try {

                recognition.stop();

            } catch (error) {

                console.error(
                    "Unable to stop speech recognition:",
                    error
                );
            }

            return;
        }


        try {

            stopSpeaking();


            recognition.lang =
                SPEECH_LANGUAGES[language] ||
                "en-IN";


            setInput("");


            recognition.start();

        } catch (error) {

            console.error(
                "Unable to start voice recognition:",
                error
            );
        }
    };


    // =====================================================
    // BACKEND TEXT TO SPEECH
    // =====================================================

    const speakResponse = async (text) => {

        if (
            !speechEnabled ||
            !text ||
            !text.trim()
        ) {

            return;
        }


        try {

            // Stop previous audio
            stopSpeaking();


            console.log(
                "Generating backend TTS:",
                {
                    language,
                    text
                }
            );


            // Request MP3 from FastAPI
            const audioBlob =
                await generateAssistantSpeech(
                    text,
                    language
                );


            if (!audioBlob) {

                throw new Error(
                    "No audio received from TTS server."
                );
            }


            // Create temporary browser URL
            const audioUrl =
                URL.createObjectURL(
                    audioBlob
                );


            const audio =
                new Audio(audioUrl);


            // Store audio reference
            speechAudioRef.current =
                audio;


            audio.volume = 1;


            audio.onended = () => {

                URL.revokeObjectURL(
                    audioUrl
                );

                speechAudioRef.current =
                    null;
            };


            audio.onerror = (event) => {

                console.error(
                    "Backend TTS audio error:",
                    event
                );

                URL.revokeObjectURL(
                    audioUrl
                );

                speechAudioRef.current =
                    null;
            };


            await audio.play();


        } catch (error) {

            console.error(
                "Backend TTS failed:",
                error
            );

            speechAudioRef.current =
                null;
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


        if (isListening) {

            try {

                recognitionRef.current?.stop();

            } catch (error) {

                console.log(error);
            }
        }


        stopSpeaking();


        // -------------------------------------------------
        // USER MESSAGE
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

            // -------------------------------------------------
            // AI RESPONSE
            // -------------------------------------------------

            const result =
                await sendAssistantMessage(
                    message,
                    language
                );


            const responseText =
                formatResponse(
                    result?.response
                );


            const finalResponse =
                responseText ||
                getErrorMessage(language);


            // -------------------------------------------------
            // ADD AI RESPONSE TO CHAT
            // -------------------------------------------------

            setMessages((previous) => [

                ...previous,

                {
                    role: "assistant",
                    content: finalResponse
                }

            ]);


            // -------------------------------------------------
            // BACKEND VOICE RESPONSE
            // -------------------------------------------------

            if (speechEnabled) {

                await speakResponse(
                    finalResponse
                );
            }


        } catch (error) {

            console.error(
                "Assistant error:",
                error
            );


            let errorMessage =
                getErrorMessage(language);


            const detail =
                error?.response?.data?.detail;


            if (
                typeof detail === "string" &&
                detail.trim()
            ) {

                errorMessage =
                    detail;
            }


            if (
                error?.response?.status === 401
            ) {

                errorMessage =
                    language === "Kannada"
                        ? "ನಿಮ್ಮ ಲಾಗಿನ್ ಅವಧಿ ಮುಗಿದಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಲಾಗಿನ್ ಮಾಡಿ."

                        : language === "Hindi"
                            ? "आपका लॉगिन समाप्त हो गया है। कृपया फिर से लॉगिन करें।"

                            : "Your login session has expired. Please login again.";
            }


            if (
                error?.response?.status === 404
            ) {

                errorMessage =
                    "AI Assistant endpoint was not found. Please check the deployed backend URL.";
            }


            if (
                error?.response?.status === 500
            ) {

                errorMessage =
                    "The AI Assistant server encountered an error. Please check the backend configuration.";
            }


            if (
                error?.message === "Network Error"
            ) {

                errorMessage =
                    "Cannot connect to the backend. Please check the backend server and API URL.";
            }


            setMessages((previous) => [

                ...previous,

                {
                    role: "assistant",
                    content: errorMessage,
                    error: true
                }

            ]);

        } finally {

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

            } catch (error) {

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
                TOP BAR
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
                LANGUAGE BAR
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
                CHAT AREA
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

                                {message.role === "user"
                                    ? "You"
                                    : "🌱 AI Assistant"}

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
                    onClick={() => {

                        setSpeechEnabled(
                            (previous) =>
                                !previous
                        );

                        if (speechEnabled) {

                            stopSpeaking();
                        }

                    }}
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


                <div className="input-bottom-row">

                    <span className="character-count">
                        {input.length}/2000
                    </span>


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
                            ? "Thinking..."
                            : "Send ➤"}

                    </button>

                </div>

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