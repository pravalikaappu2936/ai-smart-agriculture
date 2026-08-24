import React from "react";
import { useNavigate } from "react-router-dom";

import "./BackToDashboard.css";

function BackToDashboard() {

    const navigate = useNavigate();

    return (
        <button
            type="button"
            className="back-dashboard-button"
            onClick={() => navigate("/dashboard")}
            aria-label="Back to Dashboard"
        >
            <span className="back-dashboard-arrow">
                ←
            </span>

            <span className="back-dashboard-text">
                Back to Dashboard
            </span>
        </button>
    );
}

export default BackToDashboard;