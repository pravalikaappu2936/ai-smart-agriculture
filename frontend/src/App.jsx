import {
    BrowserRouter,
    Routes,
    Route,
    Navigate
} from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";

import Dashboard from "./pages/Dashboard";
import Crop from "./pages/Crop";
import Soil from "./pages/Soil";
import Fertilizer from "./pages/Fertilizer";
import Irrigation from "./pages/Irrigation";
import Weather from "./pages/Weather";
import IoT from "./pages/IoT";
import Profile from "./pages/Profile";
import Assistant from "./pages/Assistant";
import YieldPrediction from "./pages/YieldPrediction";
import MarketPrice from "./pages/MarketPrice";

import "./App.css";


function App() {

    return (

        <BrowserRouter>

            <Routes>

                {/* =================================================
                    DEFAULT
                ================================================= */}

                <Route
                    path="/"
                    element={
                        <Navigate
                            to="/login"
                            replace
                        />
                    }
                />


                {/* =================================================
                    AUTHENTICATION
                ================================================= */}

                <Route
                    path="/login"
                    element={<Login />}
                />

                <Route
                    path="/register"
                    element={<Register />}
                />


                {/* =================================================
                    MAIN APPLICATION
                ================================================= */}

                <Route
                    path="/dashboard"
                    element={<Dashboard />}
                />

                <Route
                    path="/crop"
                    element={<Crop />}
                />

                <Route
                    path="/soil"
                    element={<Soil />}
                />

                <Route
                    path="/fertilizer"
                    element={<Fertilizer />}
                />

                <Route
                    path="/irrigation"
                    element={<Irrigation />}
                />


                {/* =================================================
                    CROP YIELD PREDICTION
                ================================================= */}

                <Route
                    path="/yield"
                    element={<YieldPrediction />}
                />


                {/* =================================================
                    MARKET PRICE ANALYSIS
                ================================================= */}

                <Route
                    path="/market"
                    element={<MarketPrice />}
                />


                {/* =================================================
                    WEATHER
                ================================================= */}

                <Route
                    path="/weather"
                    element={<Weather />}
                />


                {/* =================================================
                    IOT
                ================================================= */}

                <Route
                    path="/iot"
                    element={<IoT />}
                />


                {/* =================================================
                    PROFILE
                ================================================= */}

                <Route
                    path="/profile"
                    element={<Profile />}
                />


                {/* =================================================
                    AI AGRICULTURE ASSISTANT
                ================================================= */}

                <Route
                    path="/assistant"
                    element={<Assistant />}
                />


                {/* =================================================
                    UNKNOWN URL
                ================================================= */}

                <Route
                    path="*"
                    element={
                        <Navigate
                            to="/login"
                            replace
                        />
                    }
                />

            </Routes>

        </BrowserRouter>

    );
}


export default App;