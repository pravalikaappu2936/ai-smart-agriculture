import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Login.css";

const API_URL =
    import.meta.env.VITE_API_URL ||
    "https://ai-smart-agriculture-jf61.onrender.com";

function Login() {
    const navigate = useNavigate();

    const [phoneNumber, setPhoneNumber] = useState("");
    const [password, setPassword] = useState("");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // ========================================
    // CLEAR LOGIN FORM WHEN PAGE OPENS
    // ========================================

    useEffect(() => {
        setPhoneNumber("");
        setPassword("");
        setError("");

        // Remove temporary login form values
        sessionStorage.removeItem("loginPhone");
        sessionStorage.removeItem("loginPassword");
    }, []);

    // ========================================
    // LOGIN
    // ========================================

    const handleLogin = async (e) => {
        e.preventDefault();

        setLoading(true);
        setError("");

        try {
            // ====================================
            // VALIDATION
            // ====================================

            if (!phoneNumber.trim()) {
                setError("Please enter your phone number.");
                setLoading(false);
                return;
            }

            if (!password) {
                setError("Please enter your password.");
                setLoading(false);
                return;
            }

            // ====================================
            // FASTAPI LOGIN FORM
            // ====================================

            const formData = new URLSearchParams();

            formData.append(
                "username",
                phoneNumber.trim()
            );

            formData.append(
                "password",
                password
            );

            // ====================================
            // API REQUEST
            // ====================================

            const response = await fetch(
                `${API_URL}/auth/login`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/x-www-form-urlencoded",
                    },

                    body: formData,
                }
            );

            const data = await response.json();

            console.log(
                "Login response:",
                data
            );

            // ====================================
            // LOGIN ERROR
            // ====================================

            if (!response.ok) {
                let message = "Login failed.";

                if (Array.isArray(data.detail)) {
                    message = data.detail
                        .map((item) =>
                            typeof item === "object"
                                ? item.msg || "Invalid input."
                                : item
                        )
                        .join("\n");
                }

                else if (
                    typeof data.detail === "string"
                ) {
                    message = data.detail;
                }

                setError(message);

                return;
            }

            // ====================================
            // CHECK TOKEN
            // ====================================

            if (!data.access_token) {
                setError(
                    "Login succeeded but no access token was received."
                );

                return;
            }

            // ====================================
            // SAVE AUTH TOKEN
            // ====================================

            localStorage.setItem(
                "token",
                data.access_token
            );

            // ====================================
            // CLEAR LOGIN FORM
            // ====================================

            setPhoneNumber("");
            setPassword("");
            setError("");

            // ====================================
            // GO TO DASHBOARD
            // ====================================

            navigate("/dashboard");

        }

        catch (err) {

            console.error(
                "Login error:",
                err
            );

            setError(
                "Unable to connect to the backend."
            );
        }

        finally {
            setLoading(false);
        }
    };

    // ========================================
    // LOGOUT / LOGIN PAGE FORM
    // ========================================

    return (
        <div className="login-page">

            <div className="login-container">

                {/* LOGO */}

                <div className="login-logo">

                    🌾

                    <span>
                        Smart Agriculture
                    </span>

                </div>


                {/* TITLE */}

                <h1>
                    Login
                </h1>


                {/* LOGIN FORM */}

                <form
                    onSubmit={handleLogin}
                    autoComplete="off"
                >

                    {/* PHONE NUMBER */}

                    <div className="form-group">

                        <label htmlFor="phoneNumber">
                            Phone Number
                        </label>

                        <input
                            id="phoneNumber"
                            name="login-phone"
                            type="tel"
                            value={phoneNumber}
                            onChange={(e) =>
                                setPhoneNumber(
                                    e.target.value
                                )
                            }
                            placeholder="Enter your phone number"
                            autoComplete="off"
                            required
                        />

                    </div>


                    {/* PASSWORD */}

                    <div className="form-group">

                        <label htmlFor="password">
                            Password
                        </label>

                        <input
                            id="password"
                            name="login-password"
                            type="password"
                            value={password}
                            onChange={(e) =>
                                setPassword(
                                    e.target.value
                                )
                            }
                            placeholder="Enter your password"
                            autoComplete="new-password"
                            required
                        />

                    </div>


                    {/* ERROR */}

                    {error && (

                        <div className="login-error">
                            {error}
                        </div>

                    )}


                    {/* LOGIN BUTTON */}

                    <button
                        type="submit"
                        disabled={loading}
                    >

                        {loading
                            ? "Logging in..."
                            : "Login"}

                    </button>

                </form>


                {/* REGISTER */}

                <p className="register-link">

                    New Farmer?{" "}

                    <Link to="/register">
                        Register
                    </Link>

                </p>

            </div>

        </div>
    );
}

export default Login;