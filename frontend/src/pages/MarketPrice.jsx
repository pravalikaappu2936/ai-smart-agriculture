import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getMarketPrices } from "../services/api";
import "./MarketPrice.css";

const MarketPrice = () => {
    const [commodity, setCommodity] = useState("");
    const [state, setState] = useState("Karnataka");
    const [district, setDistrict] = useState("");
    const [market, setMarket] = useState("");

    const [records, setRecords] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [isKannada, setIsKannada] = useState(false);
    const [lastUpdated, setLastUpdated] = useState(null);

    const commodities = [
        "Paddy(Common)",
        "Maize",
        "Wheat",
        "Cotton",
        "Groundnut",
        "Tomato",
        "Onion",
        "Potato",
        "Sugarcane",
        "Soyabean",
        "Chilli",
    ];

    const states = [
        "Andhra Pradesh",
        "Karnataka",
        "Telangana",
        "Tamil Nadu",
        "Maharashtra",
        "Madhya Pradesh",
        "Gujarat",
        "Rajasthan",
        "Uttar Pradesh",
        "Punjab",
        "Haryana",
        "West Bengal",
        "Odisha",
        "Kerala",
    ];

    const karnatakaDistricts = [
        "Bagalkot",
        "Ballari",
        "Belagavi",
        "Bengaluru Rural",
        "Bengaluru Urban",
        "Bidar",
        "Chamarajanagar",
        "Chikkaballapur",
        "Chikkamagaluru",
        "Chitradurga",
        "Dakshina Kannada",
        "Davanagere",
        "Dharwad",
        "Gadag",
        "Hassan",
        "Haveri",
        "Kalaburagi",
        "Kodagu",
        "Kolar",
        "Koppal",
        "Mandya",
        "Mysuru",
        "Raichur",
        "Ramanagara",
        "Shivamogga",
        "Tumakuru",
        "Udupi",
        "Uttara Kannada",
        "Vijayapura",
        "Yadgir",
        "Vijayanagara",
    ];

    const fetchPrices = async () => {
        setLoading(true);
        setError("");

        try {
            const response = await getMarketPrices({
                commodity,
                state,
                district,
                market,
                limit: 100,
            });

            if (response?.success) {
                setRecords(response.records || []);
                setLastUpdated(new Date());
            } else {
                setRecords([]);

                setError(
                    isKannada
                        ? "ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು ಲಭ್ಯವಿಲ್ಲ."
                        : "Market prices are not available."
                );
            }
        } catch (err) {
            console.error("Market price error:", err);

            setRecords([]);

            setError(
                err?.response?.data?.detail ||
                    (
                        isKannada
                            ? "ಮಾರುಕಟ್ಟೆ ಮಾಹಿತಿಯನ್ನು ಪಡೆಯಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ."
                            : "Unable to fetch market information."
                    )
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPrices();
    }, []);

    /*
     * District list
     */
    const availableDistricts = useMemo(() => {
        if (state === "Karnataka") {
            return karnatakaDistricts;
        }

        const districts = records
            .map((record) => record.district)
            .filter(Boolean)
            .map((item) => item.trim());

        return [...new Set(districts)].sort((a, b) =>
            a.localeCompare(b)
        );
    }, [records, state]);

    /*
     * Market list from currently loaded government records.
     */
    const availableMarkets = useMemo(() => {
        const markets = records
            .map((record) => record.market)
            .filter(Boolean)
            .map((item) => item.trim());

        return [...new Set(markets)].sort((a, b) =>
            a.localeCompare(b)
        );
    }, [records]);

    /*
     * Summary
     */
    const summary = useMemo(() => {
        if (!records.length) {
            return {
                min: 0,
                max: 0,
                modal: 0,
            };
        }

        const minPrices = records
            .map((r) => Number(r.min_price))
            .filter(Number.isFinite);

        const maxPrices = records
            .map((r) => Number(r.max_price))
            .filter(Number.isFinite);

        const modalPrices = records
            .map((r) => Number(r.modal_price))
            .filter(Number.isFinite);

        return {
            min: minPrices.length
                ? Math.min(...minPrices)
                : 0,

            max: maxPrices.length
                ? Math.max(...maxPrices)
                : 0,

            modal: modalPrices.length
                ? Math.round(
                      modalPrices.reduce(
                          (a, b) => a + b,
                          0
                      ) / modalPrices.length
                  )
                : 0,
        };
    }, [records]);

    /*
     * Best market based on highest MODAL PRICE.
     */
    const bestMarket = useMemo(() => {
        if (!records.length) {
            return null;
        }

        const validRecords = records.filter(
            (record) =>
                Number.isFinite(
                    Number(record.modal_price)
                )
        );

        if (!validRecords.length) {
            return null;
        }

        return [...validRecords].sort(
            (a, b) =>
                Number(b.modal_price) -
                Number(a.modal_price)
        )[0];
    }, [records]);

    /*
     * Latest arrival date.
     */
    const latestArrivalDate = useMemo(() => {
        if (!records.length) {
            return null;
        }

        const validDates = records
            .map((record) => record.arrival_date)
            .filter(Boolean);

        if (!validDates.length) {
            return null;
        }

        const convertDate = (dateString) => {
            const parts = String(dateString).split("/");

            if (parts.length === 3) {
                const [day, month, year] = parts;

                return `${year}-${month.padStart(
                    2,
                    "0"
                )}-${day.padStart(2, "0")}`;
            }

            return String(dateString);
        };

        return [...validDates].sort(
            (a, b) =>
                new Date(convertDate(b)) -
                new Date(convertDate(a))
        )[0];
    }, [records]);

    const formatPrice = (price) => {
        if (
            price === null ||
            price === undefined ||
            price === ""
        ) {
            return "—";
        }

        const value = Number(price);

        if (!Number.isFinite(value)) {
            return "—";
        }

        return `₹${value.toLocaleString("en-IN")}`;
    };

    const clearFilters = () => {
        setCommodity("");
        setState("Karnataka");
        setDistrict("");
        setMarket("");
    };

    const handleStateChange = (value) => {
        setState(value);
        setDistrict("");
        setMarket("");
    };

    const handleDistrictChange = (value) => {
        setDistrict(value);
        setMarket("");
    };

    return (
        <div className="market-page">
            <div className="market-container">

                {/* Header */}
                <div className="market-topbar">

                    <Link
                        to="/dashboard"
                        className="market-back-button"
                    >
                        ←{" "}
                        {isKannada
                            ? "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್"
                            : "Dashboard"}
                    </Link>

                    <div className="market-language">

                        <button
                            className={
                                !isKannada
                                    ? "active"
                                    : ""
                            }
                            onClick={() =>
                                setIsKannada(false)
                            }
                        >
                            English
                        </button>

                        <button
                            className={
                                isKannada
                                    ? "active"
                                    : ""
                            }
                            onClick={() =>
                                setIsKannada(true)
                            }
                        >
                            ಕನ್ನಡ
                        </button>

                    </div>
                </div>

                {/* Heading */}
                <div className="market-heading">

                    <div className="market-heading-icon">
                        📈
                    </div>

                    <div>

                        <h1>
                            {isKannada
                                ? "ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ವಿಶ್ಲೇಷಣೆ"
                                : "Market Price Analysis"}
                        </h1>

                        <p>
                            {isKannada
                                ? "ಸರ್ಕಾರದ ಮಂಡಿ ಮಾಹಿತಿಯ ಆಧಾರದ ಮೇಲೆ ಇತ್ತೀಚಿನ ಬೆಲೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ."
                                : "Check latest government mandi prices and find the best market for your crop."}
                        </p>

                    </div>

                </div>

                {/* Filters */}
                <section className="market-filter-card">

                    <div className="market-section-title">

                        <span>🔎</span>

                        <div>

                            <h2>
                                {isKannada
                                    ? "ಮಾರುಕಟ್ಟೆ ಹುಡುಕಿ"
                                    : "Find Market Prices"}
                            </h2>

                            <p>
                                {isKannada
                                    ? "ಬೆಳೆ ಮತ್ತು ಪ್ರದೇಶವನ್ನು ಆಯ್ಕೆಮಾಡಿ"
                                    : "Select crop and location"}
                            </p>

                        </div>

                    </div>

                    <div className="market-filter-grid">

                        {/* Commodity */}
                        <div className="market-field">

                            <label>
                                🌾{" "}
                                {isKannada
                                    ? "ಬೆಳೆ"
                                    : "Commodity"}
                            </label>

                            <select
                                value={commodity}
                                onChange={(e) =>
                                    setCommodity(
                                        e.target.value
                                    )
                                }
                            >

                                <option value="">
                                    {isKannada
                                        ? "ಎಲ್ಲಾ ಬೆಳೆಗಳು"
                                        : "All Commodities"}
                                </option>

                                {commodities.map(
                                    (item) => (
                                        <option
                                            key={item}
                                            value={item}
                                        >
                                            {item}
                                        </option>
                                    )
                                )}

                            </select>

                        </div>

                        {/* State */}
                        <div className="market-field">

                            <label>
                                📍{" "}
                                {isKannada
                                    ? "ರಾಜ್ಯ"
                                    : "State"}
                            </label>

                            <select
                                value={state}
                                onChange={(e) =>
                                    handleStateChange(
                                        e.target.value
                                    )
                                }
                            >

                                <option value="">
                                    {isKannada
                                        ? "ಎಲ್ಲಾ ರಾಜ್ಯಗಳು"
                                        : "All States"}
                                </option>

                                {states.map(
                                    (item) => (
                                        <option
                                            key={item}
                                            value={item}
                                        >
                                            {item}
                                        </option>
                                    )
                                )}

                            </select>

                        </div>

                        {/* District */}
                        <div className="market-field">

                            <label>
                                🏘️{" "}
                                {isKannada
                                    ? "ಜಿಲ್ಲೆ"
                                    : "District"}
                            </label>

                            <select
                                value={district}
                                onChange={(e) =>
                                    handleDistrictChange(
                                        e.target.value
                                    )
                                }
                            >

                                <option value="">
                                    {isKannada
                                        ? "ಎಲ್ಲಾ ಜಿಲ್ಲೆಗಳು"
                                        : "All Districts"}
                                </option>

                                {availableDistricts.map(
                                    (item) => (
                                        <option
                                            key={item}
                                            value={item}
                                        >
                                            {item}
                                        </option>
                                    )
                                )}

                            </select>

                        </div>

                        {/* Market */}
                        <div className="market-field">

                            <label>
                                🏪{" "}
                                {isKannada
                                    ? "ಮಾರುಕಟ್ಟೆ"
                                    : "Market"}
                            </label>

                            <select
                                value={market}
                                onChange={(e) =>
                                    setMarket(
                                        e.target.value
                                    )
                                }
                            >

                                <option value="">
                                    {isKannada
                                        ? "ಎಲ್ಲಾ ಮಾರುಕಟ್ಟೆಗಳು"
                                        : "All Markets"}
                                </option>

                                {availableMarkets.map(
                                    (item) => (
                                        <option
                                            key={item}
                                            value={item}
                                        >
                                            {item}
                                        </option>
                                    )
                                )}

                            </select>

                        </div>

                    </div>

                    <div className="market-filter-actions">

                        <button
                            className="market-search-button"
                            onClick={fetchPrices}
                            disabled={loading}
                        >
                            {loading
                                ? "⏳ Loading..."
                                : `🔍 ${
                                      isKannada
                                          ? "ಬೆಲೆ ಹುಡುಕಿ"
                                          : "Search Prices"
                                  }`}
                        </button>

                        <button
                            className="market-clear-button"
                            onClick={() => {
                                clearFilters();

                                setTimeout(
                                    fetchPrices,
                                    0
                                );
                            }}
                            disabled={loading}
                        >
                            ↻{" "}
                            {isKannada
                                ? "ಮರುಹೊಂದಿಸಿ"
                                : "Reset"}
                        </button>

                    </div>

                </section>

                {/* Error */}
                {error && (
                    <div className="market-error">
                        ⚠️ {error}
                    </div>
                )}

                {/* Results */}
                {records.length > 0 && (
                    <>

                        {/* Summary */}
                        <section className="market-summary-grid">

                            <div className="market-summary-card">

                                <span className="summary-icon">
                                    📉
                                </span>

                                <div>

                                    <p>
                                        {isKannada
                                            ? "ಕನಿಷ್ಠ ಬೆಲೆ"
                                            : "Minimum Price"}
                                    </p>

                                    <strong>
                                        {formatPrice(
                                            summary.min
                                        )}
                                    </strong>

                                </div>

                            </div>

                            <div className="market-summary-card">

                                <span className="summary-icon">
                                    💰
                                </span>

                                <div>

                                    <p>
                                        {isKannada
                                            ? "ಸರಾಸರಿ ಮೋಡಲ್ ಬೆಲೆ"
                                            : "Average Modal Price"}
                                    </p>

                                    <strong>
                                        {formatPrice(
                                            summary.modal
                                        )}
                                    </strong>

                                </div>

                            </div>

                            <div className="market-summary-card">

                                <span className="summary-icon">
                                    📈
                                </span>

                                <div>

                                    <p>
                                        {isKannada
                                            ? "ಗರಿಷ್ಠ ಬೆಲೆ"
                                            : "Maximum Price"}
                                    </p>

                                    <strong>
                                        {formatPrice(
                                            summary.max
                                        )}
                                    </strong>

                                </div>

                            </div>

                            <div className="market-summary-card">

                                <span className="summary-icon">
                                    🏪
                                </span>

                                <div>

                                    <p>
                                        {isKannada
                                            ? "ಮಾರುಕಟ್ಟೆಗಳು"
                                            : "Markets Found"}
                                    </p>

                                    <strong>
                                        {records.length}
                                    </strong>

                                </div>

                            </div>

                        </section>

                        {/* Best Market */}
                        {bestMarket && (
                            <section className="best-market-card">

                                <div className="best-market-icon">
                                    🏆
                                </div>

                                <div className="best-market-content">

                                    <span>
                                        {isKannada
                                            ? "ಬೆಳೆಯಲು ಅತ್ಯುತ್ತಮ ಮಾರುಕಟ್ಟೆ"
                                            : "Best Market to Sell"}
                                    </span>

                                    <h2>
                                        {bestMarket.market ||
                                            "Market"}
                                    </h2>

                                    <p>
                                        {bestMarket.commodity ||
                                            commodity ||
                                            "Commodity"}
                                        {" • "}
                                        {bestMarket.district ||
                                            district ||
                                            "District"}
                                        {" • "}
                                        {bestMarket.state ||
                                            state ||
                                            "State"}
                                    </p>

                                </div>

                                <div className="best-market-price">

                                    {formatPrice(
                                        bestMarket.modal_price
                                    )}

                                    <small>
                                        / quintal
                                    </small>

                                </div>

                            </section>
                        )}

                        {/* Latest Mandi Date */}
                        {latestArrivalDate && (
                            <div className="market-latest-info">
                                📅{" "}
                                <strong>
                                    {isKannada
                                        ? "ಇತ್ತೀಚಿನ ಮಂಡಿ ದಿನಾಂಕ:"
                                        : "Latest Mandi Date:"}
                                </strong>{" "}
                                {latestArrivalDate}
                            </div>
                        )}

                        {/* Table */}
                        <section className="market-results-card">

                            <div className="market-results-header">

                                <div>

                                    <h2>
                                        {isKannada
                                            ? "ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು"
                                            : "Market Prices"}
                                    </h2>

                                    <p>
                                        {isKannada
                                            ? `${records.length} ದಾಖಲೆಗಳು`
                                            : `${records.length} market records`}
                                    </p>

                                </div>

                                <button
                                    className="refresh-market-button"
                                    onClick={fetchPrices}
                                    disabled={loading}
                                >
                                    🔄{" "}
                                    {isKannada
                                        ? "ರಿಫ್ರೆಶ್"
                                        : "Refresh"}
                                </button>

                            </div>

                            <div className="market-table-wrapper">

                                <table className="market-table">

                                    <thead>

                                        <tr>

                                            <th>
                                                {isKannada
                                                    ? "ರಾಜ್ಯ"
                                                    : "State"}
                                            </th>

                                            <th>
                                                {isKannada
                                                    ? "ಜಿಲ್ಲೆ"
                                                    : "District"}
                                            </th>

                                            <th>
                                                {isKannada
                                                    ? "ಮಾರುಕಟ್ಟೆ"
                                                    : "Market"}
                                            </th>

                                            <th>
                                                {isKannada
                                                    ? "ಬೆಳೆ"
                                                    : "Commodity"}
                                            </th>

                                            <th>
                                                {isKannada
                                                    ? "ವಿಧ"
                                                    : "Variety"}
                                            </th>

                                            <th>
                                                {isKannada
                                                    ? "ಆಗಮನ ದಿನಾಂಕ"
                                                    : "Arrival Date"}
                                            </th>

                                            <th>
                                                {isKannada
                                                    ? "ಕನಿಷ್ಠ"
                                                    : "Min"}
                                            </th>

                                            <th>
                                                {isKannada
                                                    ? "ಗರಿಷ್ಠ"
                                                    : "Max"}
                                            </th>

                                            <th>
                                                {isKannada
                                                    ? "ಮೋಡಲ್"
                                                    : "Modal"}
                                            </th>

                                        </tr>

                                    </thead>

                                    <tbody>

                                        {records.map(
                                            (record, index) => (
                                                <tr
                                                    key={`${record.market}-${record.commodity}-${index}`}
                                                >

                                                    <td>
                                                        {record.state ||
                                                            "—"}
                                                    </td>

                                                    <td>
                                                        {record.district ||
                                                            "—"}
                                                    </td>

                                                    <td>
                                                        <strong>
                                                            {record.market ||
                                                                "—"}
                                                        </strong>
                                                    </td>

                                                    <td>
                                                        {record.commodity ||
                                                            "—"}
                                                    </td>

                                                    <td>
                                                        {record.variety ||
                                                            "—"}
                                                    </td>

                                                    <td>
                                                        {record.arrival_date ||
                                                            "—"}
                                                    </td>

                                                    <td>
                                                        {formatPrice(
                                                            record.min_price
                                                        )}
                                                    </td>

                                                    <td>
                                                        {formatPrice(
                                                            record.max_price
                                                        )}
                                                    </td>

                                                    <td className="modal-price">
                                                        {formatPrice(
                                                            record.modal_price
                                                        )}
                                                    </td>

                                                </tr>
                                            )
                                        )}

                                    </tbody>

                                </table>

                            </div>

                        </section>

                    </>
                )}

                {/* Empty */}
                {!loading &&
                    !error &&
                    records.length === 0 && (
                        <div className="market-empty">

                            <div>🌾</div>

                            <h2>
                                {isKannada
                                    ? "ಮಾರುಕಟ್ಟೆ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ"
                                    : "No Market Data Found"}
                            </h2>

                            <p>
                                {isKannada
                                    ? "ಬೇರೆ ಬೆಳೆ ಅಥವಾ ಪ್ರದೇಶವನ್ನು ಆಯ್ಕೆಮಾಡಿ."
                                    : "Try another commodity or location."}
                            </p>

                        </div>
                    )}

                {/* Footer */}
                <div className="market-source-info">

                    <span>
                        🇮🇳{" "}
                        {isKannada
                            ? "ಸರ್ಕಾರಿ ಮಂಡಿ ಬೆಲೆ ಮಾಹಿತಿ"
                            : "Latest Government Mandi Prices"}
                    </span>

                    {latestArrivalDate && (
                        <span>
                            {isKannada
                                ? "ಇತ್ತೀಚಿನ ಡೇಟಾ:"
                                : "Latest data:"}{" "}
                            {latestArrivalDate}
                        </span>
                    )}

                    {lastUpdated && (
                        <span>
                            {isKannada
                                ? "ಪಡೆದ ಸಮಯ:"
                                : "Retrieved:"}{" "}
                            {lastUpdated.toLocaleTimeString()}
                        </span>
                    )}

                </div>

            </div>
        </div>
    );
};

export default MarketPrice;