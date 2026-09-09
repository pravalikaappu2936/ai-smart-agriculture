import React, { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { predictPlantDisease } from "../services/api";
import "./PlantDisease.css";


// =========================================================
// PLANT DISEASE DETECTION
// =========================================================

const TEXT = {
    en: {
        title: "Plant Disease Detection",
        subtitle:
            "Upload a plant leaf image to identify possible diseases and get treatment guidance.",

        backDashboard: "← Back to Dashboard",

        uploadTitle: "Upload Plant Leaf Image",
        uploadDescription:
            "Choose a clear image of a plant leaf for disease detection.",

        chooseImage: "Choose Image",
        changeImage: "Change Image",
        removeImage: "Remove Image",

        supported:
            "Supported formats: JPG, JPEG, PNG • Maximum size: 5 MB",

        predict: "Detect Disease",
        detecting: "Analyzing Image...",

        resultTitle: "Disease Detection Result",

        crop: "Crop",
        disease: "Detected Disease",
        confidence: "Confidence",
        treatment: "Treatment",
        prevention: "Prevention",

        modelInformation: "Model Information",
        model: "Model",
        accuracy: "Validation Accuracy",
        datasetImages: "Images Used",
        classes: "Disease Classes",

        uploadFirst:
            "Please upload a plant leaf image first.",

        error:
            "Unable to analyze the image. Please try again.",

        healthy:
            "Healthy",

        diseaseDetected:
            "Disease Detected",

        noResult:
            "Upload an image and click Detect Disease to see the result.",
    },

    kn: {
        title: "ಸಸ್ಯ ರೋಗ ಪತ್ತೆ",
        subtitle:
            "ಸಸ್ಯದ ಎಲೆಯ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ರೋಗವನ್ನು ಗುರುತಿಸಿ ಮತ್ತು ಚಿಕಿತ್ಸೆಯ ಮಾಹಿತಿಯನ್ನು ಪಡೆಯಿರಿ.",

        backDashboard: "← ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗೆ ಹಿಂತಿರುಗಿ",

        uploadTitle: "ಸಸ್ಯದ ಎಲೆಯ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        uploadDescription:
            "ರೋಗ ಪತ್ತೆಗಾಗಿ ಸ್ಪಷ್ಟವಾದ ಸಸ್ಯದ ಎಲೆಯ ಚಿತ್ರವನ್ನು ಆಯ್ಕೆಮಾಡಿ.",

        chooseImage: "ಚಿತ್ರ ಆಯ್ಕೆಮಾಡಿ",
        changeImage: "ಚಿತ್ರ ಬದಲಾಯಿಸಿ",
        removeImage: "ಚಿತ್ರ ತೆಗೆದುಹಾಕಿ",

        supported:
            "ಬೆಂಬಲಿತ ಫಾರ್ಮ್ಯಾಟ್‌ಗಳು: JPG, JPEG, PNG • ಗರಿಷ್ಠ ಗಾತ್ರ: 5 MB",

        predict: "ರೋಗ ಪತ್ತೆ ಮಾಡಿ",
        detecting: "ಚಿತ್ರವನ್ನು ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...",

        resultTitle: "ರೋಗ ಪತ್ತೆ ಫಲಿತಾಂಶ",

        crop: "ಬೆಳೆ",
        disease: "ಪತ್ತೆಯಾದ ರೋಗ",
        confidence: "ವಿಶ್ವಾಸಾರ್ಹತೆ",
        treatment: "ಚಿಕಿತ್ಸೆ",
        prevention: "ತಡೆಗಟ್ಟುವಿಕೆ",

        modelInformation: "ಮಾದರಿ ಮಾಹಿತಿ",
        model: "ಮಾದರಿ",
        accuracy: "ಮೌಲ್ಯಮಾಪನ ನಿಖರತೆ",
        datasetImages: "ಬಳಸಿದ ಚಿತ್ರಗಳು",
        classes: "ರೋಗ ವರ್ಗಗಳು",

        uploadFirst:
            "ಮೊದಲು ಸಸ್ಯದ ಎಲೆಯ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",

        error:
            "ಚಿತ್ರವನ್ನು ವಿಶ್ಲೇಷಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",

        healthy:
            "ಆರೋಗ್ಯಕರ",

        diseaseDetected:
            "ರೋಗ ಪತ್ತೆಯಾಗಿದೆ",

        noResult:
            "ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಮತ್ತು ಫಲಿತಾಂಶವನ್ನು ನೋಡಲು ರೋಗ ಪತ್ತೆ ಬಟನ್ ಒತ್ತಿರಿ.",
    },
};


// =========================================================
// DISEASE NAME TRANSLATION
// =========================================================

const KANNADA_DISEASE_NAMES = {
    "Apple Scab": "ಆಪಲ್ ಸ್ಕ್ಯಾಬ್",
    "Apple Black Rot": "ಆಪಲ್ ಬ್ಲ್ಯಾಕ್ ರಾಟ್",
    "Apple Cedar Apple Rust": "ಆಪಲ್ ಸೀಡರ್ ಆಪಲ್ ರಸ್ಟ್",
    "Healthy Apple": "ಆರೋಗ್ಯಕರ ಆಪಲ್",

    "Healthy Blueberry": "ಆರೋಗ್ಯಕರ ಬ್ಲೂಬೆರ್ರಿ",

    "Cherry Powdery Mildew": "ಚೆರ್ರಿ ಪೌಡರಿ ಮಿಲ್ಡ್ಯೂ",
    "Healthy Cherry": "ಆರೋಗ್ಯಕರ ಚೆರ್ರಿ",

    "Corn Cercospora Leaf Spot Gray Leaf Spot":
        "ಜೋಳದ ಸೆರ್ಕೋಸ್ಪೋರಾ ಎಲೆ ಕಲೆ",

    "Corn Common Rust": "ಜೋಳದ ಕಾಮನ್ ರಸ್ಟ್",

    "Corn Northern Leaf Blight":
        "ಜೋಳದ ನಾರ್ದರ್ನ್ ಲೀಫ್ ಬ್ಲೈಟ್",

    "Healthy Corn": "ಆರೋಗ್ಯಕರ ಜೋಳ",

    "Grape Black Rot": "ದ್ರಾಕ್ಷಿಯ ಬ್ಲ್ಯಾಕ್ ರಾಟ್",
    "Grape Esca Black Measles":
        "ದ್ರಾಕ್ಷಿಯ ಎಸ್ಕಾ",

    "Grape Leaf Blight Isariopsis Leaf Spot":
        "ದ್ರಾಕ್ಷಿಯ ಲೀಫ್ ಬ್ಲೈಟ್",

    "Healthy Grape": "ಆರೋಗ್ಯಕರ ದ್ರಾಕ್ಷಿ",

    "Orange Huanglongbing Citrus Greening":
        "ಕಿತ್ತಳೆಯ ಸಿಟ್ರಸ್ ಗ್ರೀನಿಂಗ್",

    "Peach Bacterial Spot": "ಪೀಚ್ ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಸ್ಪಾಟ್",
    "Healthy Peach": "ಆರೋಗ್ಯಕರ ಪೀಚ್",

    "Bell Pepper Bacterial Spot":
        "ಬೆಲ್ ಪೆಪ್ಪರ್ ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಸ್ಪಾಟ್",

    "Healthy Bell Pepper": "ಆರೋಗ್ಯಕರ ಬೆಲ್ ಪೆಪ್ಪರ್",

    "Potato Early Blight": "ಆಲೂಗಡ್ಡೆಯ ಆರಂಭಿಕ ಬ್ಲೈಟ್",
    "Potato Late Blight": "ಆಲೂಗಡ್ಡೆಯ ತಡವಾದ ಬ್ಲೈಟ್",
    "Healthy Potato": "ಆರೋಗ್ಯಕರ ಆಲೂಗಡ್ಡೆ",

    "Healthy Raspberry": "ಆರೋಗ್ಯಕರ ರಾಸ್ಪ್ಬೆರಿ",

    "Healthy Soybean": "ಆರೋಗ್ಯಕರ ಸೋಯಾಬೀನ್",

    "Squash Powdery Mildew":
        "ಸ್ಕ್ವಾಷ್ ಪೌಡರಿ ಮಿಲ್ಡ್ಯೂ",

    "Strawberry Leaf Scorch":
        "ಸ್ಟ್ರಾಬೆರಿ ಲೀಫ್ ಸ್ಕಾರ್ಚ",

    "Healthy Strawberry": "ಆರೋಗ್ಯಕರ ಸ್ಟ್ರಾಬೆರಿ",

    "Tomato Bacterial Spot":
        "ಟೊಮೆಟೊ ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಸ್ಪಾಟ್",

    "Tomato Early Blight":
        "ಟೊಮೆಟೊ ಆರಂಭಿಕ ಬ್ಲೈಟ್",

    "Tomato Late Blight":
        "ಟೊಮೆಟೊ ತಡವಾದ ಬ್ಲೈಟ್",

    "Tomato Leaf Mold":
        "ಟೊಮೆಟೊ ಲೀಫ್ ಮೋಲ್ಡ್",

    "Tomato Septoria Leaf Spot":
        "ಟೊಮೆಟೊ ಸೆಪ್ಟೋರಿಯಾ ಎಲೆ ಕಲೆ",

    "Tomato Spider Mites":
        "ಟೊಮೆಟೊ ಸ್ಪೈಡರ್ ಮೈಟ್ಸ್",

    "Tomato Target Spot":
        "ಟೊಮೆಟೊ ಟಾರ್ಗೆಟ್ ಸ್ಪಾಟ್",

    "Tomato Yellow Leaf Curl Virus":
        "ಟೊಮೆಟೊ ಯೆಲ್ಲೋ ಲೀಫ್ ಕರ್ಳ್ ವೈರಸ್",

    "Tomato Mosaic Virus":
        "ಟೊಮೆಟೊ ಮೊಸಾಯಿಕ್ ವೈರಸ್",

    "Healthy Tomato":
        "ಆರೋಗ್ಯಕರ ಟೊಮೆಟೊ",
};


// =========================================================
// FORMAT DISEASE NAME
// =========================================================

const formatDiseaseName = (name) => {
    if (!name) {
        return "";
    }

    return name
        .replace(/_/g, " ")
        .replace(/\s+/g, " ")
        .trim();
};


// =========================================================
// COMPONENT
// =========================================================

const PlantDisease = () => {

    const [language, setLanguage] = useState("en");

    const [selectedImage, setSelectedImage] =
        useState(null);

    const [previewUrl, setPreviewUrl] =
        useState("");

    const [result, setResult] =
        useState(null);

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");

    const fileInputRef =
        useRef(null);


    const t = TEXT[language];


    // =====================================================
    // IMAGE SELECTION
    // =====================================================

    const handleImageChange = (event) => {

        const file =
            event.target.files?.[0];

        if (!file) {
            return;
        }


        setError("");
        setResult(null);


        // -------------------------------------------------
        // Validate file type
        // -------------------------------------------------

        if (!file.type.startsWith("image/")) {

            setError(
                "Please select a valid image file."
            );

            return;

        }


        // -------------------------------------------------
        // Validate file size
        // -------------------------------------------------

        const maxSize =
            5 * 1024 * 1024;

        if (file.size > maxSize) {

            setError(
                "Image size must be less than 5 MB."
            );

            return;

        }


        // -------------------------------------------------
        // Create preview
        // -------------------------------------------------

        const url =
            URL.createObjectURL(file);

        setSelectedImage(file);
        setPreviewUrl(url);

    };


    // =====================================================
    // REMOVE IMAGE
    // =====================================================

    const handleRemoveImage = () => {

        if (previewUrl) {

            URL.revokeObjectURL(
                previewUrl
            );

        }

        setSelectedImage(null);
        setPreviewUrl("");
        setResult(null);
        setError("");


        if (fileInputRef.current) {

            fileInputRef.current.value = "";

        }

    };


    // =====================================================
    // PREDICT DISEASE
    // =====================================================

    const handlePrediction = async () => {

        if (!selectedImage) {

            setError(t.uploadFirst);

            return;

        }


        setLoading(true);
        setError("");
        setResult(null);


        try {

            const data =
                await predictPlantDisease(
                    selectedImage
                );


            if (!data?.success) {

                throw new Error(
                    "Disease prediction failed."
                );

            }


            setResult(data);

        }

        catch (predictionError) {

            console.error(
                "Plant Disease Prediction Error:",
                predictionError
            );


            const backendMessage =
                predictionError?.response?.data?.detail;


            setError(
                backendMessage ||
                predictionError?.message ||
                t.error
            );

        }

        finally {

            setLoading(false);

        }

    };


    // =====================================================
    // GET DISPLAY DISEASE NAME
    // =====================================================

    const getDiseaseName = () => {

        if (!result?.disease) {
            return "";
        }


        const formatted =
            formatDiseaseName(
                result.disease
            );


        if (language === "kn") {

            return (
                KANNADA_DISEASE_NAMES[
                    formatted
                ] || formatted
            );

        }


        return formatted;

    };


    // =====================================================
    // HEALTH STATUS
    // =====================================================

    const isHealthy =
        result &&
        result.disease &&
        result.disease
            .toLowerCase()
            .includes("healthy");


    // =====================================================
    // RENDER
    // =====================================================

    return (

        <div
            className="plant-disease-page"
            lang={
                language === "kn"
                    ? "kn"
                    : "en"
            }
        >

            {/* =========================================
                HEADER
            ========================================= */}

            <header className="disease-header">

                <div className="disease-header-left">

                    <Link
                        to="/dashboard"
                        className="disease-back-button"
                    >
                        {t.backDashboard}
                    </Link>

                </div>


                <div className="disease-language-buttons">

                    <button
                        type="button"
                        className={
                            language === "en"
                                ? "language-btn active"
                                : "language-btn"
                        }
                        onClick={() =>
                            setLanguage("en")
                        }
                    >
                        English
                    </button>

                    <button
                        type="button"
                        className={
                            language === "kn"
                                ? "language-btn active"
                                : "language-btn"
                        }
                        onClick={() =>
                            setLanguage("kn")
                        }
                    >
                        ಕನ್ನಡ
                    </button>

                </div>

            </header>


            {/* =========================================
                MAIN
            ========================================= */}

            <main className="disease-main">

                <section className="disease-hero">

                    <div className="disease-hero-icon">
                        🌿
                    </div>

                    <div>

                        <h1>
                            {t.title}
                        </h1>

                        <p>
                            {t.subtitle}
                        </p>

                    </div>

                </section>


                <div className="disease-grid">

                    {/* =====================================
                        UPLOAD CARD
                    ===================================== */}

                    <section className="disease-card upload-card">

                        <div className="card-title-row">

                            <div className="card-icon">
                                📷
                            </div>

                            <div>

                                <h2>
                                    {t.uploadTitle}
                                </h2>

                                <p>
                                    {t.uploadDescription}
                                </p>

                            </div>

                        </div>


                        {/* =================================
                            IMAGE PREVIEW
                        ================================= */}

                        {previewUrl ? (

                            <div className="image-preview-container">

                                <img
                                    src={previewUrl}
                                    alt="Selected plant leaf"
                                    className="plant-preview-image"
                                />

                                <div className="image-actions">

                                    <button
                                        type="button"
                                        className="secondary-btn"
                                        onClick={() =>
                                            fileInputRef.current?.click()
                                        }
                                    >
                                        🔄 {t.changeImage}
                                    </button>

                                    <button
                                        type="button"
                                        className="remove-btn"
                                        onClick={
                                            handleRemoveImage
                                        }
                                    >
                                        🗑️ {t.removeImage}
                                    </button>

                                </div>

                            </div>

                        ) : (

                            <button
                                type="button"
                                className="upload-zone"
                                onClick={() =>
                                    fileInputRef.current?.click()
                                }
                            >

                                <div className="upload-icon">
                                    🌱
                                </div>

                                <strong>
                                    {t.chooseImage}
                                </strong>

                                <span>
                                    {t.supported}
                                </span>

                            </button>

                        )}


                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/png,image/jpeg,image/jpg"
                            onChange={
                                handleImageChange
                            }
                            hidden
                        />


                        {/* =================================
                            PREDICT BUTTON
                        ================================= */}

                        <button
                            type="button"
                            className="predict-btn"
                            disabled={
                                !selectedImage ||
                                loading
                            }
                            onClick={
                                handlePrediction
                            }
                        >

                            {loading ? (

                                <>
                                    <span className="spinner"></span>
                                    {t.detecting}
                                </>

                            ) : (

                                <>
                                    🔍 {t.predict}
                                </>

                            )}

                        </button>


                        {/* =================================
                            ERROR
                        ================================= */}

                        {error && (

                            <div className="disease-error">

                                ⚠️ {error}

                            </div>

                        )}

                    </section>


                    {/* =====================================
                        RESULT CARD
                    ===================================== */}

                    <section className="disease-card result-card">

                        <div className="card-title-row">

                            <div className="card-icon">
                                🧪
                            </div>

                            <div>

                                <h2>
                                    {t.resultTitle}
                                </h2>

                                <p>
                                    {result
                                        ? (
                                            isHealthy
                                                ? t.healthy
                                                : t.diseaseDetected
                                        )
                                        : t.noResult}
                                </p>

                            </div>

                        </div>


                        {result ? (

                            <div className="result-content">

                                {/* =================================
                                    MAIN RESULT
                                ================================= */}

                                <div
                                    className={
                                        isHealthy
                                            ? "status-box healthy"
                                            : "status-box disease"
                                    }
                                >

                                    <div className="status-icon">

                                        {isHealthy
                                            ? "🌿"
                                            : "🦠"}

                                    </div>

                                    <div>

                                        <span>
                                            {t.disease}
                                        </span>

                                        <strong>
                                            {getDiseaseName()}
                                        </strong>

                                    </div>

                                </div>


                                {/* =================================
                                    BASIC INFORMATION
                                ================================= */}

                                <div className="result-info-grid">

                                    <div className="info-box">

                                        <span>
                                            🌱 {t.crop}
                                        </span>

                                        <strong>
                                            {result.crop}
                                        </strong>

                                    </div>


                                    <div className="info-box">

                                        <span>
                                            📊 {t.confidence}
                                        </span>

                                        <strong>
                                            {Number(
                                                result.confidence
                                            ).toFixed(2)}
                                            %
                                        </strong>

                                    </div>

                                </div>


                                {/* =================================
                                    CONFIDENCE BAR
                                ================================= */}

                                <div className="confidence-section">

                                    <div className="confidence-header">

                                        <span>
                                            {t.confidence}
                                        </span>

                                        <strong>
                                            {Number(
                                                result.confidence
                                            ).toFixed(2)}
                                            %
                                        </strong>

                                    </div>

                                    <div className="confidence-bar">

                                        <div
                                            className="confidence-fill"
                                            style={{
                                                width: `${Math.min(
                                                    Math.max(
                                                        Number(
                                                            result.confidence
                                                        ) || 0,
                                                        0
                                                    ),
                                                    100
                                                )}%`,
                                            }}
                                        />

                                    </div>

                                </div>


                                {/* =================================
                                    TREATMENT
                                ================================= */}

                                <div className="guidance-box treatment-box">

                                    <div className="guidance-icon">
                                        💊
                                    </div>

                                    <div>

                                        <h3>
                                            {t.treatment}
                                        </h3>

                                        <p>
                                            {result.treatment}
                                        </p>

                                    </div>

                                </div>


                                {/* =================================
                                    PREVENTION
                                ================================= */}

                                <div className="guidance-box prevention-box">

                                    <div className="guidance-icon">
                                        🛡️
                                    </div>

                                    <div>

                                        <h3>
                                            {t.prevention}
                                        </h3>

                                        <p>
                                            {result.prevention}
                                        </p>

                                    </div>

                                </div>

                            </div>

                        ) : (

                            <div className="empty-result">

                                <div className="empty-result-icon">
                                    🌱
                                </div>

                                <p>
                                    {t.noResult}
                                </p>

                            </div>

                        )}

                    </section>

                </div>


                {/* =========================================
                    MODEL INFORMATION
                ========================================= */}

                <section className="disease-card model-card">

                    <div className="card-title-row">

                        <div className="card-icon">
                            🤖
                        </div>

                        <div>

                            <h2>
                                {t.modelInformation}
                            </h2>

                            <p>
                                MobileNetV3-Small
                            </p>

                        </div>

                    </div>


                    <div className="model-info-grid">

                        <div className="model-info-box">

                            <span>
                                🤖 {t.model}
                            </span>

                            <strong>
                                {result?.model ||
                                    "MobileNetV3-Small"}
                            </strong>

                        </div>


                        <div className="model-info-box">

                            <span>
                                📈 {t.accuracy}
                            </span>

                            <strong>
                                {result?.model_accuracy
                                    ? `${Number(
                                        result.model_accuracy
                                    ).toFixed(2)}%`
                                    : "93.77%"}
                            </strong>

                        </div>


                        <div className="model-info-box">

                            <span>
                                🖼️ {t.datasetImages}
                            </span>

                            <strong>
                                {result?.dataset_images_used ||
                                    "11,400"}
                            </strong>

                        </div>


                        <div className="model-info-box">

                            <span>
                                🔢 {t.classes}
                            </span>

                            <strong>
                                {result?.total_classes ||
                                    "38"}
                            </strong>

                        </div>

                    </div>

                </section>

            </main>

        </div>

    );

};


export default PlantDisease;