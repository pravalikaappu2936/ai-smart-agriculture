import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Profile.css";

const API_URL =
    import.meta.env.VITE_API_URL ||
    "https://ai-smart-agriculture-jf61.onrender.com";

function Profile() {
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    const token = localStorage.getItem("token");

    if (!token) {
      navigate("/");
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/users/me`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (response.status === 401) {
        localStorage.removeItem("token");
        navigate("/");
        return;
      }

      if (!response.ok) {
        throw new Error(
          data.detail ||
          "Unable to load profile."
        );
      }

      setProfile(data);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <div className="profile-container">

      <div className="profile-header">

        <div className="profile-avatar">
          👨‍🌾
        </div>

        <h1>
          My Profile
        </h1>

        <p>
          Smart Agriculture account information
        </p>

      </div>

      {loading && (
        <div className="profile-loading">
          Loading profile...
        </div>
      )}

      {error && (
        <div className="profile-error">
          {error}
        </div>
      )}

      {profile && (
        <div className="profile-card">

          <div className="profile-field">
            <span className="profile-label">
              User ID
            </span>

            <span className="profile-value">
              {profile.id}
            </span>
          </div>

          <div className="profile-field">
            <span className="profile-label">
              Username
            </span>

            <span className="profile-value">
              {profile.username}
            </span>
          </div>

          <div className="profile-field">
            <span className="profile-label">
              Phone Number
            </span>

            <span className="profile-value">
              {profile.phone_number}
            </span>
          </div>

        </div>
      )}

      <div className="profile-actions">

        <button
          className="profile-dashboard-btn"
          onClick={() => navigate("/dashboard")}
        >
          ← Dashboard
        </button>

        <button
          className="profile-logout-btn"
          onClick={handleLogout}
        >
          Logout
        </button>

      </div>

    </div>
  );
}

export default Profile;

