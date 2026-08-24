import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Register.css";

const API_URL = "http://127.0.0.1:8000";

function Register() {
    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [phoneNumber, setPhoneNumber] = useState("");
    const [password, setPassword] = useState("");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    // ========================================
    // CLEAR FORM WHEN REGISTER PAGE OPENS
    // ========================================

    useEffect(() => {
        setUsername("");
        setPhoneNumber("");
        setPassword("");
        setError("");
        setSuccess("");

        // Make sure we don't keep temporary
        // registration information.
        sessionStorage.removeItem("registerUsername");
        sessionStorage.removeItem("registerPhone");
        sessionStorage.removeItem("registerPassword");
    }, []);

    // ========================================
    // REGISTER
    // ========================================

    const handleRegister = async (e) => {
        e.preventDefault();

        setLoading(true);
        setError("");
        setSuccess("");

        try {
            const response = await fetch(
                `${API_URL}/auth/register`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                    },

                    body: JSON.stringify({
                        username: username.trim(),
                        phone_number: phoneNumber.trim(),
                        password: password,
                    }),
                }
            );

            const data = await response.json();

            console.log("Register response:", data);

            // ====================================
            // REGISTRATION ERROR
            // ====================================

            if (!response.ok) {
                let message = "Registration failed.";

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
            // SUCCESS
            // ====================================

            setSuccess(
                "Registration successful. Redirecting to login..."
            );

            // Clear form after successful registration
            setUsername("");
            setPhoneNumber("");
            setPassword("");

            // ====================================
            // REDIRECT TO LOGIN
            // ====================================

            setTimeout(() => {
                navigate("/");
            }, 1500);
        }

        catch (err) {
            console.error(
                "Registration error:",
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

    return (
        <div className="register-page">

            <div className="register-container">

                {/* LOGO */}

                <div className="register-logo">

                    🌾

                    <span>
                        Smart Agriculture
                    </span>

                </div>


                {/* TITLE */}

                <h1>
                    Create Account
                </h1>


                {/* SUBTITLE */}

                <p className="register-subtitle">
                    Register to access Smart Agriculture.
                </p>


                {/* REGISTER FORM */}

                <form
                    onSubmit={handleRegister}
                    autoComplete="off"
                >

                    {/* USERNAME */}

                    <div className="register-form-group">

                        <label htmlFor="username">
                            Username
                        </label>

                        <input
                            id="username"
                            name="register-username"
                            type="text"
                            value={username}
                            onChange={(e) =>
                                setUsername(
                                    e.target.value
                                )
                            }
                            placeholder="Enter your username"
                            autoComplete="off"
                            required
                        />

                    </div>


                    {/* PHONE NUMBER */}

                    <div className="register-form-group">

                        <label htmlFor="phoneNumber">
                            Phone Number
                        </label>

                        <input
                            id="phoneNumber"
                            name="register-phone"
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

                    <div className="register-form-group">

                        <label htmlFor="password">
                            Password
                        </label>

                        <input
                            id="password"
                            name="register-password"
                            type="password"
                            value={password}
                            onChange={(e) =>
                                setPassword(
                                    e.target.value
                                )
                            }
                            placeholder="Create a password"
                            autoComplete="new-password"
                            required
                        />

                    </div>


                    {/* ERROR */}

                    {error && (
                        <div className="register-error">
                            {error}
                        </div>
                    )}


                    {/* SUCCESS */}

                    {success && (
                        <div className="register-success">
                            {success}
                        </div>
                    )}


                    {/* REGISTER BUTTON */}

                    <button
                        type="submit"
                        disabled={loading}
                    >
                        {loading
                            ? "Creating Account..."
                            : "Register"}
                    </button>

                </form>


                {/* LOGIN LINK */}

                <p className="login-link">

                    Already have an account?{" "}

                    <Link to="/">
                        Login
                    </Link>

                </p>

            </div>

        </div>
    );
}

export default Register;