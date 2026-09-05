import React, { useState } from "react";
import { predictCropYield } from "../services/api";
import "./YieldPrediction.css";

const STATES = [
  "Andhra Pradesh",
  "Bihar",
  "Gujarat",
  "Haryana",
  "Karnataka",
  "Madhya Pradesh",
  "Maharashtra",
  "Punjab",
  "Rajasthan",
  "Tamil Nadu",
  "Telangana",
  "Uttar Pradesh",
  "West Bengal",
];

const CROPS = [
  "Rice",
  "Wheat",
  "Maize",
  "Cotton",
  "Sugarcane",
  "Groundnut",
  "Soybean",
  "Potato",
  "Tomato",
  "Chickpea",
];

const SEASONS = [
  "Kharif",
  "Rabi",
  "Summer",
  "Whole Year",
];

export default function YieldPrediction() {
  const [formData, setFormData] = useState({
    year: new Date().getFullYear(),
    state: "",
    crop: "",
    season: "",
    area: "",
    annual_rainfall: "",
    fertilizer: "",
    pesticide: "",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setResult(null);

    try {
      setLoading(true);

      const payload = {
        year: Number(formData.year),
        state: formData.state.trim(),
        crop: formData.crop.trim(),
        season: formData.season.trim(),
        area: Number(formData.area),
        annual_rainfall: Number(formData.annual_rainfall),
        fertilizer: Number(formData.fertilizer),
        pesticide: Number(formData.pesticide),
      };

      const response = await predictCropYield(payload);

      setResult(response.data || response);
    } catch (err) {
      console.error("Yield prediction error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to predict crop yield. Please check the entered values."
      );
    } finally {
      setLoading(false);
    }
  };

  const getCategoryClass = (category) => {
    if (!category) return "";

    const value = category.toLowerCase();

    if (value === "high") return "yield-high";
    if (value === "moderate") return "yield-moderate";
    return "yield-low";
  };

  return (
    <div className="yield-page">
      <div className="yield-container">

        <div className="yield-header">
          <div>
            <h1>🌾 Crop Yield Prediction</h1>
            <p>
              Predict expected crop yield using soil, rainfall,
              agricultural input and crop information.
            </p>
          </div>
        </div>

        <div className="yield-content">

          {/* INPUT SECTION */}
          <div className="yield-card">
            <div className="card-title">
              <h2>🌱 Farm Information</h2>
              <p>Enter the details of your crop and farming conditions.</p>
            </div>

            <form onSubmit={handleSubmit}>

              <div className="form-grid">

                <div className="form-group">
                  <label>Year</label>
                  <input
                    type="number"
                    name="year"
                    value={formData.year}
                    onChange={handleChange}
                    min="2000"
                    max="2100"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>State</label>
                  <select
                    name="state"
                    value={formData.state}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select State</option>

                    {STATES.map((state) => (
                      <option key={state} value={state}>
                        {state}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Crop</label>
                  <select
                    name="crop"
                    value={formData.crop}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select Crop</option>

                    {CROPS.map((crop) => (
                      <option key={crop} value={crop}>
                        {crop}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Season</label>
                  <select
                    name="season"
                    value={formData.season}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select Season</option>

                    {SEASONS.map((season) => (
                      <option key={season} value={season}>
                        {season}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Area (hectares)</label>
                  <input
                    type="number"
                    name="area"
                    value={formData.area}
                    onChange={handleChange}
                    min="0.01"
                    step="0.01"
                    placeholder="Example: 100"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Annual Rainfall (mm)</label>
                  <input
                    type="number"
                    name="annual_rainfall"
                    value={formData.annual_rainfall}
                    onChange={handleChange}
                    min="0"
                    step="0.01"
                    placeholder="Example: 800"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Fertilizer (kg)</label>
                  <input
                    type="number"
                    name="fertilizer"
                    value={formData.fertilizer}
                    onChange={handleChange}
                    min="0"
                    step="0.01"
                    placeholder="Example: 100000"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Pesticide (kg)</label>
                  <input
                    type="number"
                    name="pesticide"
                    value={formData.pesticide}
                    onChange={handleChange}
                    min="0"
                    step="0.01"
                    placeholder="Example: 500"
                    required
                  />
                </div>

              </div>

              {error && (
                <div className="yield-error">
                  ⚠️ {error}
                </div>
              )}

              <button
                type="submit"
                className="predict-yield-btn"
                disabled={loading}
              >
                {loading
                  ? "🔄 Predicting..."
                  : "🌾 Predict Crop Yield"}
              </button>

            </form>
          </div>

          {/* RESULT */}
          {result && (
            <div className="yield-result-card">

              <div className="result-title">
                <h2>📊 Yield Prediction Result</h2>
                <span className={getCategoryClass(result.yield_category)}>
                  {result.yield_category}
                </span>
              </div>

              <div className="main-yield-result">
                <span className="yield-number">
                  {Number(result.predicted_yield).toFixed(2)}
                </span>

                <span className="yield-unit">
                  {result.unit || "tonnes/hectare"}
                </span>
              </div>

              <div className="result-grid">

                <div className="result-item">
                  <span>Crop</span>
                  <strong>{formData.crop}</strong>
                </div>

                <div className="result-item">
                  <span>State</span>
                  <strong>{formData.state}</strong>
                </div>

                <div className="result-item">
                  <span>Season</span>
                  <strong>{formData.season}</strong>
                </div>

                <div className="result-item">
                  <span>Model R²</span>
                  <strong>
                    {result.r2 !== undefined
                      ? Number(result.r2).toFixed(3)
                      : "N/A"}
                  </strong>
                </div>

                <div className="result-item">
                  <span>MAE</span>
                  <strong>
                    {result.mae !== undefined
                      ? Number(result.mae).toFixed(2)
                      : "N/A"}
                  </strong>
                </div>

                <div className="result-item">
                  <span>RMSE</span>
                  <strong>
                    {result.rmse !== undefined
                      ? Number(result.rmse).toFixed(2)
                      : "N/A"}
                  </strong>
                </div>

              </div>

              <div className="dataset-info">
                🤖 Prediction generated using the Random Forest Yield
                Prediction model trained on{" "}
                <strong>
                  {result.dataset_records || 17400}
                </strong>{" "}
                agricultural records.
              </div>

            </div>
          )}

        </div>
      </div>
    </div>
  );
}