import { useState } from "react";
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

    const [submitted, setSubmitted] = useState(false);

    const handleChange = (event) => {
        const { name, value } = event.target;

        setSensorData({
            ...sensorData,
            [name]: value
        });

        setSubmitted(false);
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        setSubmitted(true);
    };

    return (
        <div className="iot-page">

            <div className="iot-header">
                <h1>IoT Sensor Monitoring</h1>
                <p>
                    Monitor soil and environmental sensor values
                    for smart agriculture.
                </p>
            </div>

            <div className="iot-container">

                <form
                    className="iot-form"
                    onSubmit={handleSubmit}
                >

                    <h2>Sensor Data</h2>

                    <div className="iot-grid">

                        <div className="iot-field">
                            <label>Soil Moisture (%)</label>

                            <input
                                type="number"
                                name="soil_moisture"
                                value={sensorData.soil_moisture}
                                onChange={handleChange}
                                min="0"
                                required
                            />
                        </div>


                        <div className="iot-field">
                            <label>Temperature (°C)</label>

                            <input
                                type="number"
                                name="temperature"
                                value={sensorData.temperature}
                                onChange={handleChange}
                                required
                            />
                        </div>


                        <div className="iot-field">
                            <label>Humidity (%)</label>

                            <input
                                type="number"
                                name="humidity"
                                value={sensorData.humidity}
                                onChange={handleChange}
                                min="0"
                                max="100"
                                required
                            />
                        </div>


                        <div className="iot-field">
                            <label>Nitrogen (N)</label>

                            <input
                                type="number"
                                name="nitrogen"
                                value={sensorData.nitrogen}
                                onChange={handleChange}
                                min="0"
                                required
                            />
                        </div>


                        <div className="iot-field">
                            <label>Phosphorus (P)</label>

                            <input
                                type="number"
                                name="phosphorus"
                                value={sensorData.phosphorus}
                                onChange={handleChange}
                                min="0"
                                required
                            />
                        </div>


                        <div className="iot-field">
                            <label>Potassium (K)</label>

                            <input
                                type="number"
                                name="potassium"
                                value={sensorData.potassium}
                                onChange={handleChange}
                                min="0"
                                required
                            />
                        </div>


                        <div className="iot-field">
                            <label>Soil pH</label>

                            <input
                                type="number"
                                name="ph"
                                value={sensorData.ph}
                                onChange={handleChange}
                                min="0"
                                max="14"
                                step="0.1"
                                required
                            />
                        </div>

                    </div>


                    <button
                        type="submit"
                        className="iot-button"
                    >
                        Update Sensor Data
                    </button>

                </form>


                <div className="iot-status">

                    <h2>Live Sensor Status</h2>

                    <div className="status-indicator">
                        <span className="status-dot"></span>

                        <span>
                            Sensor System Active
                        </span>
                    </div>


                    <div className="sensor-cards">

                        <div className="sensor-card">
                            <span>Soil Moisture</span>
                            <strong>
                                {sensorData.soil_moisture || "--"} %
                            </strong>
                        </div>


                        <div className="sensor-card">
                            <span>Temperature</span>
                            <strong>
                                {sensorData.temperature || "--"} °C
                            </strong>
                        </div>


                        <div className="sensor-card">
                            <span>Humidity</span>
                            <strong>
                                {sensorData.humidity || "--"} %
                            </strong>
                        </div>


                        <div className="sensor-card">
                            <span>Nitrogen</span>
                            <strong>
                                {sensorData.nitrogen || "--"}
                            </strong>
                        </div>


                        <div className="sensor-card">
                            <span>Phosphorus</span>
                            <strong>
                                {sensorData.phosphorus || "--"}
                            </strong>
                        </div>


                        <div className="sensor-card">
                            <span>Potassium</span>
                            <strong>
                                {sensorData.potassium || "--"}
                            </strong>
                        </div>


                        <div className="sensor-card">
                            <span>Soil pH</span>
                            <strong>
                                {sensorData.ph || "--"}
                            </strong>
                        </div>

                    </div>


                    {submitted && (
                        <div className="iot-success">
                            Sensor data updated successfully.
                        </div>
                    )}

                </div>

            </div>

        </div>
    );
}

export default IoT;