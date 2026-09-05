import React, { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { predictCropYield } from "../services/api";
import "./YieldPrediction.css";

const CROPS = [
    "Arecanut",
    "Arhar/Tur",
    "Bajra",
    "Banana",
    "Barley",
    "Black pepper",
    "Cardamom",
    "Cashewnut",
    "Castor seed",
    "Coconut",
    "Coriander",
    "Cotton(lint)",
    "Cowpea(Lobia)",
    "Dry chillies",
    "Garlic",
    "Ginger",
    "Gram",
    "Groundnut",
    "Horse-gram",
    "Jowar",
    "Khesari",
    "Linseed",
    "Maize",
    "Masoor",
    "Mesta",
    "Moong(Green Gram)",
    "Niger seed",
    "Onion",
    "Other Cereals",
    "Other Kharif pulses",
    "Other Rabi pulses",
    "Peas & beans (Pulses)",
    "Potato",
    "Ragi",
    "Rapeseed &Mustard",
    "Rice",
    "Safflower",
    "Sannhamp",
    "Sesamum",
    "Small millets",
    "Soyabean",
    "Sugarcane",
    "Sunflower",
    "Sweet potato",
    "Tapioca",
    "Tobacco",
    "Tomato",
    "Turmeric",
    "Urad",
    "Wheat",
    "other oilseeds",
    "other pulses",
    "other cereals",
    "other summer crops",
    "other crops"
];

const STATES = [
    "Andaman and Nicobar Islands",
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jammu and Kashmir",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Puducherry",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal"
];

const SEASONS = [
    "Kharif",
    "Rabi",
    "Whole Year",
    "Summer",
    "Winter",
    "Autumn"
];

const TEXT = {
    en: {
        title: "Crop Yield Prediction",
        subtitle:
            "Predict crop yield using historical agricultural, rainfall and farming data.",
        back: "Back to Dashboard",

        language: "Language",
        english: "English",
        kannada: "ಕನ್ನಡ",

        cropDetails: "Crop Details",
        crop: "Crop",
        selectCrop: "Select Crop",

        state: "State",
        selectState: "Select State",

        season: "Season",
        selectSeason: "Select Season",

        year: "Year",
        area: "Cultivated Area",
        rainfall: "Annual Rainfall",
        fertilizer: "Fertilizer Used",
        pesticide: "Pesticide Used",

        areaUnit: "hectares",
        rainfallUnit: "mm",
        fertilizerUnit: "kg",
        pesticideUnit: "kg",

        agriculturalInputs: "Agricultural Inputs",

        predict: "Predict Crop Yield",
        predicting: "Predicting Yield...",

        required: "Please fill in all required fields.",
        invalidArea: "Area must be greater than zero.",
        invalidRainfall: "Rainfall cannot be negative.",
        invalidFertilizer: "Fertilizer cannot be negative.",
        invalidPesticide: "Pesticide cannot be negative.",

        predictionResult: "Prediction Result",
        predictedYield: "Predicted Yield",
        yieldCategory: "Yield Category",

        low: "Low",
        moderate: "Moderate",
        high: "High",

        predictionDetails: "Prediction Details",
        selectedCrop: "Selected Crop",
        selectedState: "Selected State",
        selectedSeason: "Selected Season",

        modelPerformance: "Model Performance",
        r2Score: "R² Score",
        mae: "MAE",
        rmse: "RMSE",
        datasetRecords: "Dataset Records",

        tonnesPerHectare: "tonnes/hectare",

        modelInfo: "Model Information",
        modelDescription:
            "Random Forest Regression model trained using historical Indian crop-yield data.",
        records: "17,400 records",
        features: "8 input features",
        algorithm: "Random Forest Regression",

        errorTitle: "Prediction Failed",
        tryAgain: "Please check the input values and try again.",

        noResult:
            "Enter the agricultural details and click the prediction button."
    },

    kn: {
        title: "ಬೆಳೆ ಇಳುವರಿ ಮುನ್ಸೂಚನೆ",
        subtitle:
            "ಐತಿಹಾಸಿಕ ಕೃಷಿ, ಮಳೆ ಮತ್ತು ಕೃಷಿ ಮಾಹಿತಿಯನ್ನು ಬಳಸಿಕೊಂಡು ಬೆಳೆ ಇಳುವರಿಯನ್ನು ಊಹಿಸಿ.",
        back: "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗೆ ಹಿಂತಿರುಗಿ",

        language: "ಭಾಷೆ",
        english: "English",
        kannada: "ಕನ್ನಡ",

        cropDetails: "ಬೆಳೆ ವಿವರಗಳು",
        crop: "ಬೆಳೆ",
        selectCrop: "ಬೆಳೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",

        state: "ರಾಜ್ಯ",
        selectState: "ರಾಜ್ಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ",

        season: "ಋತು",
        selectSeason: "ಋತುವನ್ನು ಆಯ್ಕೆಮಾಡಿ",

        year: "ವರ್ಷ",
        area: "ಬೆಳೆ ಪ್ರದೇಶ",
        rainfall: "ವಾರ್ಷಿಕ ಮಳೆ",
        fertilizer: "ಬಳಸಿದ ಗೊಬ್ಬರ",
        pesticide: "ಬಳಸಿದ ಕೀಟನಾಶಕ",

        areaUnit: "ಹೆಕ್ಟೇರ್",
        rainfallUnit: "ಮಿಮೀ",
        fertilizerUnit: "ಕೆಜಿ",
        pesticideUnit: "ಕೆಜಿ",

        agriculturalInputs: "ಕೃಷಿ ಇನ್‌ಪುಟ್‌ಗಳು",

        predict: "ಬೆಳೆ ಇಳುವರಿಯನ್ನು ಊಹಿಸಿ",
        predicting: "ಇಳುವರಿಯನ್ನು ಊಹಿಸಲಾಗುತ್ತಿದೆ...",

        required: "ದಯವಿಟ್ಟು ಅಗತ್ಯವಿರುವ ಎಲ್ಲಾ ಮಾಹಿತಿಯನ್ನು ನಮೂದಿಸಿ.",
        invalidArea: "ಬೆಳೆ ಪ್ರದೇಶವು ಶೂನ್ಯಕ್ಕಿಂತ ಹೆಚ್ಚಿರಬೇಕು.",
        invalidRainfall: "ಮಳೆಯ ಪ್ರಮಾಣವು ಋಣಾತ್ಮಕವಾಗಿರಬಾರದು.",
        invalidFertilizer: "ಗೊಬ್ಬರದ ಪ್ರಮಾಣವು ಋಣಾತ್ಮಕವಾಗಿರಬಾರದು.",
        invalidPesticide: "ಕೀಟನಾಶಕದ ಪ್ರಮಾಣವು ಋಣಾತ್ಮಕವಾಗಿರಬಾರದು.",

        predictionResult: "ಮುನ್ಸೂಚನೆ ಫಲಿತಾಂಶ",
        predictedYield: "ಊಹಿಸಲಾದ ಇಳುವರಿ",
        yieldCategory: "ಇಳುವರಿ ವರ್ಗ",

        low: "ಕಡಿಮೆ",
        moderate: "ಮಧ್ಯಮ",
        high: "ಹೆಚ್ಚು",

        predictionDetails: "ಮುನ್ಸೂಚನೆ ವಿವರಗಳು",
        selectedCrop: "ಆಯ್ಕೆ ಮಾಡಿದ ಬೆಳೆ",
        selectedState: "ಆಯ್ಕೆ ಮಾಡಿದ ರಾಜ್ಯ",
        selectedSeason: "ಆಯ್ಕೆ ಮಾಡಿದ ಋತು",

        modelPerformance: "ಮಾದರಿ ಕಾರ್ಯಕ್ಷಮತೆ",
        r2Score: "R² ಸ್ಕೋರ್",
        mae: "MAE",
        rmse: "RMSE",
        datasetRecords: "ಡೇಟಾಸೆಟ್ ದಾಖಲೆಗಳು",

        tonnesPerHectare: "ಟನ್/ಹೆಕ್ಟೇರ್",

        modelInfo: "ಮಾದರಿ ಮಾಹಿತಿ",
        modelDescription:
            "ಐತಿಹಾಸಿಕ ಭಾರತೀಯ ಬೆಳೆ ಇಳುವರಿ ಮಾಹಿತಿಯಿಂದ ತರಬೇತಿ ಪಡೆದ Random Forest Regression ಮಾದರಿ.",
        records: "17,400 ದಾಖಲೆಗಳು",
        features: "8 ಇನ್‌ಪುಟ್ ವೈಶಿಷ್ಟ್ಯಗಳು",
        algorithm: "Random Forest Regression",

        errorTitle: "ಮುನ್ಸೂಚನೆ ವಿಫಲವಾಗಿದೆ",
        tryAgain:
            "ಇನ್‌ಪುಟ್ ಮೌಲ್ಯಗಳನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",

        noResult:
            "ಕೃಷಿ ವಿವರಗಳನ್ನು ನಮೂದಿಸಿ ಮತ್ತು ಮುನ್ಸೂಚನೆ ಬಟನ್ ಕ್ಲಿಕ್ ಮಾಡಿ."
    }
};

function YieldPrediction() {
    const [language, setLanguage] = useState("en");
    const [formData, setFormData] = useState({
        year: new Date().getFullYear(),
        state: "",
        crop: "",
        season: "",
        area: "",
        annual_rainfall: "",
        fertilizer: "",
        pesticide: ""
    });

    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const t = TEXT[language];

    const cropOptions = useMemo(
        () => [...new Set(CROPS)].sort((a, b) => a.localeCompare(b)),
        []
    );

    const stateOptions = useMemo(
        () => [...STATES].sort((a, b) => a.localeCompare(b)),
        []
    );

    const handleChange = (event) => {
        const { name, value } = event.target;

        setFormData((previous) => ({
            ...previous,
            [name]: value
        }));

        setError("");
    };

    const handleSubmit = async (event) => {
        event.preventDefault();

        setError("");
        setResult(null);

        if (
            !formData.year ||
            !formData.state ||
            !formData.crop ||
            !formData.season ||
            !formData.area ||
            !formData.annual_rainfall ||
            formData.fertilizer === "" ||
            formData.pesticide === ""
        ) {
            setError(t.required);
            return;
        }

        const area = Number(formData.area);
        const rainfall = Number(formData.annual_rainfall);
        const fertilizer = Number(formData.fertilizer);
        const pesticide = Number(formData.pesticide);

        if (area <= 0) {
            setError(t.invalidArea);
            return;
        }

        if (rainfall < 0) {
            setError(t.invalidRainfall);
            return;
        }

        if (fertilizer < 0) {
            setError(t.invalidFertilizer);
            return;
        }

        if (pesticide < 0) {
            setError(t.invalidPesticide);
            return;
        }

        const payload = {
            year: Number(formData.year),
            state: formData.state,
            crop: formData.crop,
            season: formData.season,
            area,
            annual_rainfall: rainfall,
            fertilizer,
            pesticide
        };

        try {
            setLoading(true);

            const response = await predictCropYield(payload);

            setResult(response);
        } catch (err) {
            console.error("Crop yield prediction error:", err);

            setError(
                err?.response?.data?.detail ||
                err?.message ||
                t.tryAgain
            );
        } finally {
            setLoading(false);
        }
    };

    const getCategoryText = (category) => {
        if (!category) return "-";

        const normalized = String(category).toLowerCase();

        if (normalized === "low") return t.low;
        if (normalized === "moderate") return t.moderate;
        if (normalized === "high") return t.high;

        return category;
    };

    return (
        <div className="yield-page">
            <header className="yield-header">
                <div className="yield-header-left">
                    <Link
                        to="/dashboard"
                        className="yield-back-button"
                    >
                        ← {t.back}
                    </Link>
                </div>

                <div className="yield-language">
                    <span>{t.language}:</span>

                    <button
                        type="button"
                        className={
                            language === "en"
                                ? "yield-lang active"
                                : "yield-lang"
                        }
                        onClick={() => setLanguage("en")}
                    >
                        {t.english}
                    </button>

                    <button
                        type="button"
                        className={
                            language === "kn"
                                ? "yield-lang active"
                                : "yield-lang"
                        }
                        onClick={() => setLanguage("kn")}
                    >
                        {t.kannada}
                    </button>
                </div>
            </header>

            <main className="yield-container">
                <section className="yield-hero">
                    <div className="yield-hero-icon">🌾</div>

                    <div>
                        <h1>{t.title}</h1>
                        <p>{t.subtitle}</p>
                    </div>
                </section>

                <div className="yield-layout">
                    <section className="yield-form-card">
                        <div className="yield-section-title">
                            <span>🌱</span>
                            <div>
                                <h2>{t.cropDetails}</h2>
                                <p>{t.agriculturalInputs}</p>
                            </div>
                        </div>

                        <form onSubmit={handleSubmit}>
                            <div className="yield-form-grid">

                                <div className="yield-field">
                                    <label htmlFor="crop">
                                        {t.crop}
                                    </label>

                                    <select
                                        id="crop"
                                        name="crop"
                                        value={formData.crop}
                                        onChange={handleChange}
                                    >
                                        <option value="">
                                            {t.selectCrop}
                                        </option>

                                        {cropOptions.map((crop) => (
                                            <option
                                                key={crop}
                                                value={crop}
                                            >
                                                {crop}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="yield-field">
                                    <label htmlFor="state">
                                        {t.state}
                                    </label>

                                    <select
                                        id="state"
                                        name="state"
                                        value={formData.state}
                                        onChange={handleChange}
                                    >
                                        <option value="">
                                            {t.selectState}
                                        </option>

                                        {stateOptions.map((state) => (
                                            <option
                                                key={state}
                                                value={state}
                                            >
                                                {state}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="yield-field">
                                    <label htmlFor="season">
                                        {t.season}
                                    </label>

                                    <select
                                        id="season"
                                        name="season"
                                        value={formData.season}
                                        onChange={handleChange}
                                    >
                                        <option value="">
                                            {t.selectSeason}
                                        </option>

                                        {SEASONS.map((season) => (
                                            <option
                                                key={season}
                                                value={season}
                                            >
                                                {season}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="yield-field">
                                    <label htmlFor="year">
                                        {t.year}
                                    </label>

                                    <input
                                        id="year"
                                        name="year"
                                        type="number"
                                        min="2000"
                                        max="2100"
                                        value={formData.year}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="yield-field">
                                    <label htmlFor="area">
                                        {t.area}
                                    </label>

                                    <div className="yield-input-with-unit">
                                        <input
                                            id="area"
                                            name="area"
                                            type="number"
                                            min="0.01"
                                            step="0.01"
                                            placeholder="e.g. 10"
                                            value={formData.area}
                                            onChange={handleChange}
                                        />
                                        <span>
                                            {t.areaUnit}
                                        </span>
                                    </div>
                                </div>

                                <div className="yield-field">
                                    <label htmlFor="annual_rainfall">
                                        {t.rainfall}
                                    </label>

                                    <div className="yield-input-with-unit">
                                        <input
                                            id="annual_rainfall"
                                            name="annual_rainfall"
                                            type="number"
                                            min="0"
                                            step="0.1"
                                            placeholder="e.g. 1200"
                                            value={
                                                formData.annual_rainfall
                                            }
                                            onChange={handleChange}
                                        />
                                        <span>
                                            {t.rainfallUnit}
                                        </span>
                                    </div>
                                </div>

                                <div className="yield-field">
                                    <label htmlFor="fertilizer">
                                        {t.fertilizer}
                                    </label>

                                    <div className="yield-input-with-unit">
                                        <input
                                            id="fertilizer"
                                            name="fertilizer"
                                            type="number"
                                            min="0"
                                            step="0.01"
                                            placeholder="e.g. 500"
                                            value={formData.fertilizer}
                                            onChange={handleChange}
                                        />
                                        <span>
                                            {t.fertilizerUnit}
                                        </span>
                                    </div>
                                </div>

                                <div className="yield-field">
                                    <label htmlFor="pesticide">
                                        {t.pesticide}
                                    </label>

                                    <div className="yield-input-with-unit">
                                        <input
                                            id="pesticide"
                                            name="pesticide"
                                            type="number"
                                            min="0"
                                            step="0.01"
                                            placeholder="e.g. 50"
                                            value={formData.pesticide}
                                            onChange={handleChange}
                                        />
                                        <span>
                                            {t.pesticideUnit}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {error && (
                                <div className="yield-error">
                                    <span>⚠️</span>
                                    <div>
                                        <strong>
                                            {t.errorTitle}
                                        </strong>
                                        <p>{error}</p>
                                    </div>
                                </div>
                            )}

                            <button
                                type="submit"
                                className="yield-predict-button"
                                disabled={loading}
                            >
                                {loading ? (
                                    <>
                                        <span className="yield-spinner" />
                                        {t.predicting}
                                    </>
                                ) : (
                                    <>
                                        🔮 {t.predict}
                                    </>
                                )}
                            </button>
                        </form>
                    </section>

                    <aside className="yield-side-column">

                        <section className="yield-info-card">
                            <div className="yield-info-icon">
                                🤖
                            </div>

                            <h3>{t.modelInfo}</h3>

                            <p>{t.modelDescription}</p>

                            <div className="yield-info-stats">
                                <div>
                                    <strong>{t.records}</strong>
                                    <span>{t.datasetRecords}</span>
                                </div>

                                <div>
                                    <strong>{t.features}</strong>
                                    <span>{t.agriculturalInputs}</span>
                                </div>

                                <div>
                                    <strong>{t.algorithm}</strong>
                                    <span>ML Model</span>
                                </div>
                            </div>
                        </section>

                        {!result && !loading && (
                            <section className="yield-empty-card">
                                <div>📊</div>
                                <p>{t.noResult}</p>
                            </section>
                        )}
                    </aside>
                </div>

                {result && (
                    <section className="yield-result-card">
                        <div className="yield-result-header">
                            <div>
                                <span className="yield-result-icon">
                                    🌾
                                </span>

                                <div>
                                    <h2>
                                        {t.predictionResult}
                                    </h2>

                                    <p>
                                        {result.crop ||
                                            formData.crop}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="yield-main-result">
                            <span>{t.predictedYield}</span>

                            <strong>
                                {Number(
                                    result.predicted_yield ?? 0
                                ).toFixed(2)}
                            </strong>

                            <small>
                                {result.unit ||
                                    t.tonnesPerHectare}
                            </small>
                        </div>

                        <div className="yield-category">
                            <span>{t.yieldCategory}</span>

                            <strong
                                className={
                                    `yield-category-${String(
                                        result.yield_category || ""
                                    ).toLowerCase()}`
                                }
                            >
                                {getCategoryText(
                                    result.yield_category
                                )}
                            </strong>
                        </div>

                        <div className="yield-details-section">
                            <h3>{t.predictionDetails}</h3>

                            <div className="yield-details-grid">
                                <div>
                                    <span>
                                        {t.selectedCrop}
                                    </span>
                                    <strong>
                                        {formData.crop}
                                    </strong>
                                </div>

                                <div>
                                    <span>
                                        {t.selectedState}
                                    </span>
                                    <strong>
                                        {formData.state}
                                    </strong>
                                </div>

                                <div>
                                    <span>
                                        {t.selectedSeason}
                                    </span>
                                    <strong>
                                        {formData.season}
                                    </strong>
                                </div>
                            </div>
                        </div>

                        <div className="yield-performance">
                            <h3>{t.modelPerformance}</h3>

                            <div className="yield-metrics-grid">
                                <div>
                                    <span>{t.r2Score}</span>
                                    <strong>
                                        {Number(
                                            result.r2 ?? 0
                                        ).toFixed(4)}
                                    </strong>
                                </div>

                                <div>
                                    <span>{t.mae}</span>
                                    <strong>
                                        {Number(
                                            result.mae ?? 0
                                        ).toFixed(2)}
                                    </strong>
                                </div>

                                <div>
                                    <span>{t.rmse}</span>
                                    <strong>
                                        {Number(
                                            result.rmse ?? 0
                                        ).toFixed(2)}
                                    </strong>
                                </div>

                                <div>
                                    <span>
                                        {t.datasetRecords}
                                    </span>
                                    <strong>
                                        {result.dataset_records ||
                                            17400}
                                    </strong>
                                </div>
                            </div>
                        </div>
                    </section>
                )}
            </main>
        </div>
    );
}

export default YieldPrediction;

