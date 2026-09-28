// =========================================================
// API CONFIGURATION
// =========================================================

const API_URL =
    import.meta.env.VITE_API_URL ||
    "https://ai-smart-agriculture-production.up.railway.app";


// =========================================================
// HELPER FUNCTION
// =========================================================

async function handleResponse(response) {

    const data = await response.json();

    if (!response.ok) {

        throw new Error(
            data.detail ||
            data.message ||
            "Something went wrong"
        );
    }

    return data;
}


// =========================================================
// AUTHENTICATION
// =========================================================

// ---------------------------------------------------------
// LOGIN
// ---------------------------------------------------------

export async function loginUser(
    phoneNumber,
    password
) {

    const formData = new URLSearchParams();

    formData.append(
        "username",
        phoneNumber
    );

    formData.append(
        "password",
        password
    );

    const response = await fetch(
        `${API_URL}/auth/login`,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/x-www-form-urlencoded",
            },

            body: formData.toString(),
        }
    );

    return handleResponse(response);
}


// ---------------------------------------------------------
// REGISTER
// ---------------------------------------------------------

export async function registerUser(
    username,
    phoneNumber,
    password
) {

    const response = await fetch(
        `${API_URL}/auth/register`,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json",
            },

            body: JSON.stringify({
                username: username,
                phone_number: phoneNumber,
                password: password,
            }),
        }
    );

    return handleResponse(response);
}


// =========================================================
// FORGOT PASSWORD
// =========================================================

// ---------------------------------------------------------
// SEND OTP
// ---------------------------------------------------------

export async function forgotPassword(
    phoneNumber
) {

    const response = await fetch(
        `${API_URL}/auth/forgot-password?phone_number=${encodeURIComponent(
            phoneNumber
        )}`,
        {
            method: "POST",
        }
    );

    return handleResponse(response);
}


// ---------------------------------------------------------
// VERIFY RESET OTP
// ---------------------------------------------------------

export async function verifyResetOTP(
    phoneNumber,
    otp
) {

    const response = await fetch(
        `${API_URL}/auth/verify-reset-otp?phone_number=${encodeURIComponent(
            phoneNumber
        )}&otp=${encodeURIComponent(
            otp
        )}`,
        {
            method: "POST",
        }
    );

    return handleResponse(response);
}


// ---------------------------------------------------------
// RESET PASSWORD
// ---------------------------------------------------------

export async function resetPassword(
    phoneNumber,
    resetToken,
    newPassword
) {

    const response = await fetch(
        `${API_URL}/auth/reset-password?phone_number=${encodeURIComponent(
            phoneNumber
        )}&reset_token=${encodeURIComponent(
            resetToken
        )}&new_password=${encodeURIComponent(
            newPassword
        )}`,
        {
            method: "POST",
        }
    );

    return handleResponse(response);
}


// =========================================================
// TOKEN
// =========================================================

export function getToken() {

    return localStorage.getItem("token");
}


// =========================================================
// AUTH HEADERS
// =========================================================

export function getAuthHeaders() {

    const token = getToken();

    return {
        "Content-Type": "application/json",

        ...(token
            ? {
                Authorization:
                    `Bearer ${token}`
            }
            : {})
    };
}


// =========================================================
// API URL
// =========================================================

export { API_URL };