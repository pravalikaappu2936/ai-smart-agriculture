import { Link } from "react-router-dom";

function Sidebar() {
  return (
    <div
      style={{
        width: "220px",
        height: "100vh",
        background: "#2E7D32",
        color: "white",
        padding: "20px",
      }}
    >
      <h2>Menu</h2>

      <ul style={{ listStyle: "none", padding: 0 }}>
        <li><Link to="/dashboard">Dashboard</Link></li>
        <li><Link to="/crop">Crop Recommendation</Link></li>
        <li><Link to="/soil">Soil Analysis</Link></li>
        <li><Link to="/fertilizer">Fertilizer</Link></li>
        <li><Link to="/irrigation">Irrigation</Link></li>
        <li><Link to="/weather">Weather</Link></li>
        <li><Link to="/iot">IoT Dashboard</Link></li>
        <li><Link to="/profile">Profile</Link></li>
      </ul>
    </div>
  );
}

export default Sidebar;