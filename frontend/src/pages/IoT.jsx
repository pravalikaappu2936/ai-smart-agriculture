import { useCallback, useEffect, useState } from "react";
import api from "../services/api";
import "./IoT.css";

function IoT() {
    const [sensorData, setSensorData] = useState({
        soil_moisture: "",
        temperature: "",
        humidity: "",
        nitrogen: "",
        phosphorus: "",
        potassium: "",
        ph: ""
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [lastUpdated, setLastUpdated] = useState(null);

    // =====================================================
    // FETCH LATEST SENSOR DATA
    // =====================================================

    const fetchSensorData = useCallback(async () => {
        try {
            const response = await api.get("/iot/latest");

            console.log("IoT response:", response.data);

            const data = response.data;

            // -------------------------------------------------
            // Support possible backend response structures
            // -------------------------------------------------

            const sensor =
                data?.data ||
                data?.sensor_data ||
                data?.sensor ||
                data;

            if (!sensor || typeof sensor !== "object") {
                throw new Error("Invalid sensor response");
            }

            setSensorData({
                soil_moisture:
                    sensor.soil_moisture ??
                    sensor.moisture ??
                    "",

                temperature:
                    sensor.temperature ??
                    "",

                humidity:
                    sensor.humidity ??
                    "",

                nitrogen:
                    sensor.nitrogen ??
                    "",

                phosphorus:
                    sensor.phosphorus ??
                    "",

                potassium:
                    sensor.potassium ??
                    "",

                ph:
                    sensor.ph ??
                    sensor.pH ??
                    ""
            });

            setLastUpdated(new Date());
            setError("");

        } catch (err) {
            console.error(
                "Failed to fetch IoT sensor data:",
                err
            );

            if (err.response) {

                if (err.response.status === 401) {
                    setError(
                        "Authentication expired. Please login again."
                    );

                } else if (err.response.status === 429) {
                    setError(
                        "Too many sensor requests. Please wait a moment."
                    );

                } else if (err.response.status === 503) {
                    setError(
                        "Agriculture backend is temporarily unavailable."
                    );

                } else {
                    setError(
                        err.response.data?.detail ||
                        "Unable to fetch live IoT sensor data."
                    );
                }

            } else {
                setError(
                    "Unable to connect to the agriculture backend."
                );
            }
        } finally {
            setLoading(false);
        }
    }, []);

    // =====================================================
    // INITIAL FETCH + SAFE POLLING
    // =====================================================

    useEffect(() => {

        let active = true;
        let interval = null;

        const loadData = async () => {

            if (!active) {
                return;
            }

            await fetchSensorData();
        };

        // Fetch immediately
        loadData();

        // Poll only every 30 seconds
        interval = setInterval(() => {
            loadData();
        }, 30000);

        return () => {

            active = false;

            if (interval) {
                clearInterval(interval);
            }
        };

    }, [fetchSensorData]);

    // =====================================================
    // MANUAL REFRESH
    // =====================================================

    const handleRefresh = async () => {

        setLoading(true);

        await fetchSensorData();
    };

    // =====================================================
    // FORMAT LAST UPDATED
    // =====================================================

    const formatLastUpdated = () => {

        if (!lastUpdated) {
            return "Waiting for sensor data...";
        }

        return lastUpdated.toLocaleTimeString();
    };

    // =====================================================
    // CHECK SENSOR AVAILABILITY
    // =====================================================

    const hasSensorData =
        Object.values(sensorData).some(
            value =>
                value !== "" &&
                value !== null &&
                value !== undefined
        );

    // =====================================================
    // UI
    // =====================================================

    return (
        <div className="iot-page">

            <div className="iot-header">

                <h1>
                    IoT Sensor Monitoring
                </h1>

                <p>
                    Monitor soil and environmental sensor
                    values for smart agriculture.
                </p>

            </div>


            <div className="iot-container">

                {/* =================================================
                    SENSOR FORM / DATA
                ================================================= */}

                <div className="iot-form">

                    <h2>
                        Live Sensor Data
                    </h2>

                    <div className="iot-grid">

                        {/* SOIL MOISTURE */}

                        <div className="iot-field">

                            <label>
                                Soil Moisture (%)
                            </label>

                            <input
                                type="text"
                                value={
                                    sensorData.soil_moisture !== ""
                                        ? sensorData.soil_moisture
                                        : "--"
                                }
                                readOnly
                            />

                        </div>


                        {/* TEMPERATURE */}

                        <div className="iot-field">

                            <label>
                                Temperature (°C)
                            </label>

                            <input
                                type="text"
                                value={
                                    sensorData.temperature !== ""
                                        ? sensorData.temperature
                                        : "--"
                                }
                                readOnly
                            />

                        </div>


                        {/* HUMIDITY */}

                        <div className="iot-field">

                            <label>
                                Humidity (%)
                            </label>

                            <input
                                type="text"
                                value={
                                    sensorData.humidity !== ""
                                        ? sensorData.humidity
                                        : "--"
                                }
                                readOnly
                            />

                        </div>


                        {/* NITROGEN */}

                        <div className="iot-field">

                            <label>
                                Nitrogen (N)
                            </label>

                            <input
                                type="text"
                                value={
                                    sensorData.nitrogen !== ""
                                        ? sensorData.nitrogen
                                        : "--"
                                }
                                readOnly
                            />

                        </div>


                        {/* PHOSPHORUS */}

                        <div className="iot-field">

                            <label>
                                Phosphorus (P)
                            </label>

                            <input
                                type="text"
                                value={
                                    sensorData.phosphorus !== ""
                                        ? sensorData.phosphorus
                                        : "--"
                                }
                                readOnly
                            />

                        </div>


                        {/* POTASSIUM */}

                        <div className="iot-field">

                            <label>
                                Potassium (K)
                            </label>

                            <input
                                type="text"
                                value={
                                    sensorData.potassium !== ""
                                        ? sensorData.potassium
                                        : "--"
                                }
                                readOnly
                            />

                        </div>


                        {/* PH */}

                        <div className="iot-field">

                            <label>
                                Soil pH
                            </label>

                            <input
                                type="text"
                                value={
                                    sensorData.ph !== ""
                                        ? sensorData.ph
                                        : "--"
                                }
                                readOnly
                            />

                        </div>

                    </div>


                    {/* =================================================
                        REFRESH BUTTON
                    ================================================= */}

                    <button
                        type="button"
                        className="iot-button"
                        onClick={handleRefresh}
                        disabled={loading}
                    >

                        {loading
                            ? "Loading Sensors..."
                            : "Refresh Sensor Data"
                        }

                    </button>

                </div>


                {/* =================================================
                    STATUS
                ================================================= */}

                <div className="iot-status">

                    <h2>
                        Live Sensor Status
                    </h2>


                    <div className="status-indicator">

                        <span
                            className={
                                hasSensorData
                                    ? "status-dot active"
                                    : "status-dot"
                            }
                        />

                        <span>
                            {hasSensorData
                                ? "Sensor System Active"
                                : "Waiting for Sensors"
                            }
                        </span>

                    </div>


                    {/* =================================================
                        SENSOR CARDS
                    ================================================= */}

                    <div className="sensor-cards">

                        <div className="sensor-card">

                            <span>
                                Soil Moisture
                            </span>

                            <strong>
                                {sensorData.soil_moisture !== ""
                                    ? `${sensorData.soil_moisture} %`
                                    : "--"
                                }
                            </strong>

                        </div>


                        <div className="sensor-card">

                            <span>
                                Temperature
                            </span>

                            <strong>
                                {sensorData.temperature !== ""
                                    ? `${sensorData.temperature} °C`
                                    : "--"
                                }
                            </strong>

                        </div>


                        <div className="sensor-card">

                            <span>
                                Humidity
                            </span>

                            <strong>
                                {sensorData.humidity !== ""
                                    ? `${sensorData.humidity} %`
                                    : "--"
                                }
                            </strong>

                        </div>


                        <div className="sensor-card">

                            <span>
                                Nitrogen
                            </span>

                            <strong>
                                {sensorData.nitrogen !== ""
                                    ? sensorData.nitrogen
                                    : "--"
                                }
                            </strong>

                        </div>


                        <div className="sensor-card">

                            <span>
                                Phosphorus
                            </span>

                            <strong>
                                {sensorData.phosphorus !== ""
                                    ? sensorData.phosphorus
                                    : "--"
                                }
                            </strong>

                        </div>


                        <div className="sensor-card">

                            <span>
                                Potassium
                            </span>

                            <strong>
                                {sensorData.potassium !== ""
                                    ? sensorData.potassium
                                    : "--"
                                }
                            </strong>

                        </div>


                        <div className="sensor-card">

                            <span>
                                Soil pH
                            </span>

                            <strong>
                                {sensorData.ph !== ""
                                    ? sensorData.ph
                                    : "--"
                                }
                            </strong>

                        </div>

                    </div>


                    {/* =================================================
                        LAST UPDATED
                    ================================================= */}

                    <div className="last-updated">

                        Last updated:{" "}

                        <strong>
                            {formatLastUpdated()}
                        </strong>

                    </div>


                    {/* =================================================
                        ERROR
                    ================================================= */}

                    {error && (

                        <div className="iot-error">

                            {error}

                        </div>

                    )}

                </div>

            </div>

        </div>
    );
}

export default IoT;