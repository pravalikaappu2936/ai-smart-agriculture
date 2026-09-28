import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./ForgotPassword.css";

const API_URL =
    import.meta.env.VITE_API_URL ||
    "https://ai-smart-agriculture-production.up.railway.app";

function ForgotPassword() {

    const navigate = useNavigate();

    // =========================================================
    // STEP
    // =========================================================

    const [step, setStep] = useState(1);


    // =========================================================
    // FORM DATA
    // =========================================================

    const [phoneNumber, setPhoneNumber] = useState("");
    const [otp, setOtp] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");


    // =========================================================
    // RESET TOKEN
    // =========================================================

    const [resetToken, setResetToken] = useState("");


    // =========================================================
    // UI STATE
    // =========================================================

    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");


    // =========================================================
    // SEND OTP
    // =========================================================

    const handleSendOTP = async (e) => {

        e.preventDefault();

        setError("");
        setMessage("");

        if (!phoneNumber.trim()) {

            setError(
                "Please enter your phone number."
            );

            return;
        }

        setLoading(true);

        try {

            const response = await fetch(
                `${API_URL}/auth/forgot-password?phone_number=${encodeURIComponent(
                    phoneNumber.trim()
                )}`,
                {
                    method: "POST"
                }
            );

            const data = await response.json();

            if (!response.ok) {

                setError(
                    typeof data.detail === "string"
                        ? data.detail
                        : "Unable to send OTP."
                );

                return;
            }


            // =================================================
            // OTP SENT
            // =================================================
            // The OTP is intentionally NOT displayed or logged.
            // In production, the OTP should be delivered through
            // the configured SMS service.
            // =================================================

            setMessage(
                "OTP sent to your registered phone number."
            );

            setStep(2);

        } catch (err) {

            console.error(
                "Forgot password error:",
                err
            );

            setError(
                "Unable to connect to the backend."
            );

        } finally {

            setLoading(false);
        }
    };


    // =========================================================
    // VERIFY OTP
    // =========================================================

    const handleVerifyOTP = async (e) => {

        e.preventDefault();

        setError("");
        setMessage("");

        if (!otp.trim()) {

            setError(
                "Please enter the OTP."
            );

            return;
        }

        if (otp.trim().length !== 6) {

            setError(
                "OTP must be 6 digits."
            );

            return;
        }

        setLoading(true);

        try {

            const response = await fetch(
                `${API_URL}/auth/verify-reset-otp?phone_number=${encodeURIComponent(
                    phoneNumber.trim()
                )}&otp=${encodeURIComponent(
                    otp.trim()
                )}`,
                {
                    method: "POST"
                }
            );

            const data = await response.json();

            if (!response.ok) {

                setError(
                    typeof data.detail === "string"
                        ? data.detail
                        : "Invalid OTP."
                );

                return;
            }


            // =================================================
            // SAVE PASSWORD RESET TOKEN
            // =================================================

            setResetToken(
                data.reset_token
            );

            setMessage(
                "OTP verified successfully."
            );

            setStep(3);

        } catch (err) {

            console.error(
                "OTP verification error:",
                err
            );

            setError(
                "Unable to connect to the backend."
            );

        } finally {

            setLoading(false);
        }
    };


    // =========================================================
    // RESET PASSWORD
    // =========================================================

    const handleResetPassword = async (e) => {

        e.preventDefault();

        setError("");
        setMessage("");


        // =====================================================
        // VALIDATE PASSWORD
        // =====================================================

        if (!newPassword) {

            setError(
                "Please enter a new password."
            );

            return;
        }


        if (newPassword.length < 6) {

            setError(
                "Password must be at least 6 characters."
            );

            return;
        }


        if (newPassword !== confirmPassword) {

            setError(
                "Passwords do not match."
            );

            return;
        }


        setLoading(true);

        try {

            const response = await fetch(
                `${API_URL}/auth/reset-password?phone_number=${encodeURIComponent(
                    phoneNumber.trim()
                )}&reset_token=${encodeURIComponent(
                    resetToken
                )}&new_password=${encodeURIComponent(
                    newPassword
                )}`,
                {
                    method: "POST"
                }
            );

            const data = await response.json();

            if (!response.ok) {

                setError(
                    typeof data.detail === "string"
                        ? data.detail
                        : "Unable to reset password."
                );

                return;
            }


            setMessage(
                "Password reset successfully. Redirecting to login..."
            );


            // =================================================
            // REDIRECT TO LOGIN
            // =================================================

            setTimeout(() => {

                navigate("/login");

            }, 1500);

        } catch (err) {

            console.error(
                "Reset password error:",
                err
            );

            setError(
                "Unable to connect to the backend."
            );

        } finally {

            setLoading(false);
        }
    };


    // =========================================================
    // GO BACK TO PREVIOUS STEP
    // =========================================================

    const handleBack = () => {

        setError("");
        setMessage("");

        if (step === 2) {

            setOtp("");

            setStep(1);

        } else if (step === 3) {

            setNewPassword("");
            setConfirmPassword("");
            setResetToken("");

            setStep(2);
        }
    };


    // =========================================================
    // RENDER
    // =========================================================

    return (

        <div className="forgot-password-page">

            <div className="forgot-password-container">


                {/* =================================================
                    BRANDING
                    ================================================= */}

                <div className="forgot-password-branding">

                    <img
                        src="/logo.png"
                        alt="AI Smart Agriculture"
                        className="forgot-password-logo"
                    />

                    <h1 className="forgot-password-brand-title">
                        AI Smart Agriculture
                    </h1>

                    <p className="forgot-password-brand-subtitle">
                        Smart Farming • Better Tomorrow
                    </p>

                </div>


                {/* =================================================
                    STEP INDICATOR
                    ================================================= */}

                <div className="forgot-password-steps">

                    <div
                        className={`forgot-password-step ${
                            step >= 1 ? "active" : ""
                        }`}
                    >
                        1
                    </div>

                    <div
                        className={`forgot-password-step-line ${
                            step >= 2 ? "active" : ""
                        }`}
                    />

                    <div
                        className={`forgot-password-step ${
                            step >= 2 ? "active" : ""
                        }`}
                    >
                        2
                    </div>

                    <div
                        className={`forgot-password-step-line ${
                            step >= 3 ? "active" : ""
                        }`}
                    />

                    <div
                        className={`forgot-password-step ${
                            step >= 3 ? "active" : ""
                        }`}
                    >
                        3
                    </div>

                </div>


                {/* =================================================
                    STEP 1 - PHONE NUMBER
                    ================================================= */}

                {step === 1 && (

                    <>

                        <h2 className="forgot-password-heading">
                            Forgot Password
                        </h2>

                        <p className="forgot-password-description">
                            Enter your registered phone number
                            to receive an OTP.
                        </p>


                        <form
                            className="forgot-password-form"
                            onSubmit={handleSendOTP}
                            autoComplete="off"
                        >

                            <div className="forgot-password-form-group">

                                <label htmlFor="phoneNumber">
                                    Phone Number
                                </label>

                                <input
                                    id="phoneNumber"
                                    type="tel"
                                    value={phoneNumber}
                                    onChange={(e) =>
                                        setPhoneNumber(
                                            e.target.value
                                        )
                                    }
                                    placeholder="Enter your phone number"
                                    autoComplete="tel"
                                    required
                                />

                            </div>


                            {/* ERROR */}

                            {error && (

                                <div className="forgot-password-error">
                                    {error}
                                </div>

                            )}


                            {/* SUCCESS */}

                            {message && (

                                <div className="forgot-password-success">
                                    {message}
                                </div>

                            )}


                            <button
                                type="submit"
                                className="forgot-password-button"
                                disabled={loading}
                            >

                                {loading
                                    ? "Sending..."
                                    : "Send OTP"}

                            </button>

                        </form>

                    </>

                )}


                {/* =================================================
                    STEP 2 - VERIFY OTP
                    ================================================= */}

                {step === 2 && (

                    <>

                        <h2 className="forgot-password-heading">
                            Verify OTP
                        </h2>

                        <p className="forgot-password-description">
                            Enter the 6-digit OTP sent to your
                            registered phone number.
                        </p>


                        <form
                            className="forgot-password-form"
                            onSubmit={handleVerifyOTP}
                            autoComplete="off"
                        >

                            <div className="forgot-password-form-group">

                                <label htmlFor="otp">
                                    OTP
                                </label>

                                <input
                                    id="otp"
                                    type="text"
                                    inputMode="numeric"
                                    maxLength="6"
                                    value={otp}
                                    onChange={(e) =>
                                        setOtp(
                                            e.target.value.replace(
                                                /\D/g,
                                                ""
                                            )
                                        )
                                    }
                                    placeholder="Enter 6-digit OTP"
                                    autoComplete="one-time-code"
                                    className="forgot-password-otp-input"
                                    required
                                />

                            </div>


                            {/* ERROR */}

                            {error && (

                                <div className="forgot-password-error">
                                    {error}
                                </div>

                            )}


                            {/* SUCCESS */}

                            {message && (

                                <div className="forgot-password-success">
                                    {message}
                                </div>

                            )}


                            <button
                                type="submit"
                                className="forgot-password-button"
                                disabled={loading}
                            >

                                {loading
                                    ? "Verifying..."
                                    : "Verify OTP"}

                            </button>


                            <button
                                type="button"
                                className="forgot-password-button"
                                onClick={handleBack}
                                disabled={loading}
                                style={{
                                    marginTop: "10px",
                                    background: "#757575"
                                }}
                            >
                                Back
                            </button>

                        </form>

                    </>

                )}


                {/* =================================================
                    STEP 3 - NEW PASSWORD
                    ================================================= */}

                {step === 3 && (

                    <>

                        <h2 className="forgot-password-heading">
                            Create New Password
                        </h2>

                        <p className="forgot-password-description">
                            Enter and confirm your new password.
                        </p>


                        <form
                            className="forgot-password-form"
                            onSubmit={handleResetPassword}
                            autoComplete="off"
                        >

                            {/* NEW PASSWORD */}

                            <div className="forgot-password-form-group">

                                <label htmlFor="newPassword">
                                    New Password
                                </label>

                                <input
                                    id="newPassword"
                                    type="password"
                                    value={newPassword}
                                    onChange={(e) =>
                                        setNewPassword(
                                            e.target.value
                                        )
                                    }
                                    placeholder="Enter new password"
                                    autoComplete="new-password"
                                    className="forgot-password-password-input"
                                    required
                                />

                            </div>


                            {/* CONFIRM PASSWORD */}

                            <div className="forgot-password-form-group">

                                <label htmlFor="confirmPassword">
                                    Confirm Password
                                </label>

                                <input
                                    id="confirmPassword"
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) =>
                                        setConfirmPassword(
                                            e.target.value
                                        )
                                    }
                                    placeholder="Confirm new password"
                                    autoComplete="new-password"
                                    className="forgot-password-password-input"
                                    required
                                />

                            </div>


                            {/* ERROR */}

                            {error && (

                                <div className="forgot-password-error">
                                    {error}
                                </div>

                            )}


                            {/* SUCCESS */}

                            {message && (

                                <div className="forgot-password-success">
                                    {message}
                                </div>

                            )}


                            <button
                                type="submit"
                                className="forgot-password-button"
                                disabled={loading}
                            >

                                {loading
                                    ? "Resetting..."
                                    : "Reset Password"}

                            </button>


                            <button
                                type="button"
                                className="forgot-password-button"
                                onClick={handleBack}
                                disabled={loading}
                                style={{
                                    marginTop: "10px",
                                    background: "#757575"
                                }}
                            >
                                Back
                            </button>

                        </form>

                    </>

                )}


                {/* =================================================
                    BACK TO LOGIN
                    ================================================= */}

                <p className="forgot-password-back">

                    <Link to="/login">
                        Back to Login
                    </Link>

                </p>

            </div>

        </div>
    );
}

export default ForgotPassword;