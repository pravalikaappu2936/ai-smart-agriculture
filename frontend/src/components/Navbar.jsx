import { Link } from "react-router-dom";

function Navbar() {
    return (
        <nav
            style={{
                background: "#2E7D32",
                padding: "15px",
                display: "flex",
                justifyContent: "space-between",
                color: "white",
            }}
        >
            <h2>🌱 Smart Agriculture</h2>

            <div style={{ display: "flex", gap: "15px" }}>
                <Link to="/" style={{ color: "white" }}>Home</Link>
                <Link to="/login" style={{ color: "white" }}>Login</Link>
                <Link to="/register" style={{ color: "white" }}>Register</Link>
                <Link to="/dashboard" style={{ color: "white" }}>Dashboard</Link>
            </div>
        </nav>
    );
}

export default Navbar;