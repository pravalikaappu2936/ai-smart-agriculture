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

    /*
     * Commodity values must remain in the exact
     * English format expected by the government API.
     * Kannada names are only for display.
     */
    const commodities = [
        {
            value: "Paddy(Common)",
            en: "Paddy (Common)",
            kn: "ಭತ್ತ",
        },
        {
            value: "Maize",
            en: "Maize",
            kn: "ಮೆಕ್ಕೆಜೋಳ",
        },
        {
            value: "Wheat",
            en: "Wheat",
            kn: "ಗೋಧಿ",
        },
        {
            value: "Cotton",
            en: "Cotton",
            kn: "ಹತ್ತಿ",
        },
        {
            value: "Groundnut",
            en: "Groundnut",
            kn: "ಕಡಲೆಕಾಯಿ",
        },
        {
            value: "Tomato",
            en: "Tomato",
            kn: "ಟೊಮ್ಯಾಟೊ",
        },
        {
            value: "Onion",
            en: "Onion",
            kn: "ಈರುಳ್ಳಿ",
        },
        {
            value: "Potato",
            en: "Potato",
            kn: "ಆಲೂಗಡ್ಡೆ",
        },
        {
            value: "Sugarcane",
            en: "Sugarcane",
            kn: "ಕಬ್ಬು",
        },
        {
            value: "Soyabean",
            en: "Soyabean",
            kn: "ಸೋಯಾಬೀನ್",
        },
        {
            value: "Chilli",
            en: "Chilli",
            kn: "ಮೆಣಸಿನಕಾಯಿ",
        },
    ];

    /*
     * State values remain in English for the API.
     */
    const states = [
        {
            value: "Andhra Pradesh",
            en: "Andhra Pradesh",
            kn: "ಆಂಧ್ರ ಪ್ರದೇಶ",
        },
        {
            value: "Karnataka",
            en: "Karnataka",
            kn: "ಕರ್ನಾಟಕ",
        },
        {
            value: "Telangana",
            en: "Telangana",
            kn: "ತೆಲಂಗಾಣ",
        },
        {
            value: "Tamil Nadu",
            en: "Tamil Nadu",
            kn: "ತಮಿಳುನಾಡು",
        },
        {
            value: "Maharashtra",
            en: "Maharashtra",
            kn: "ಮಹಾರಾಷ್ಟ್ರ",
        },
        {
            value: "Madhya Pradesh",
            en: "Madhya Pradesh",
            kn: "ಮಧ್ಯ ಪ್ರದೇಶ",
        },
        {
            value: "Gujarat",
            en: "Gujarat",
            kn: "ಗುಜರಾತ್",
        },
        {
            value: "Rajasthan",
            en: "Rajasthan",
            kn: "ರಾಜಸ್ಥಾನ",
        },
        {
            value: "Uttar Pradesh",
            en: "Uttar Pradesh",
            kn: "ಉತ್ತರ ಪ್ರದೇಶ",
        },
        {
            value: "Punjab",
            en: "Punjab",
            kn: "ಪಂಜಾಬ್",
        },
        {
            value: "Haryana",
            en: "Haryana",
            kn: "ಹರಿಯಾಣ",
        },
        {
            value: "West Bengal",
            en: "West Bengal",
            kn: "ಪಶ್ಚಿಮ ಬಂಗಾಳ",
        },
        {
            value: "Odisha",
            en: "Odisha",
            kn: "ಒಡಿಶಾ",
        },
        {
            value: "Kerala",
            en: "Kerala",
            kn: "ಕೇರಳ",
        },
    ];

    /*
     * IMPORTANT:
     * These are the exact district names currently
     * available in backend/data/market_cache.json.
     *
     * Do not change the English values because they
     * are used for API filtering.
     */
    const karnatakaDistricts = [
        {
            value: "Bagalkot",
            en: "Bagalkot",
            kn: "ಬಾಗಲಕೋಟೆ",
        },
        {
            value: "Belagavi",
            en: "Belagavi",
            kn: "ಬೆಳಗಾವಿ",
        },
        {
            value: "Bellary",
            en: "Bellary",
            kn: "ಬಳ್ಳಾರಿ",
        },
        {
            value: "Bengaluru",
            en: "Bengaluru",
            kn: "ಬೆಂಗಳೂರು",
        },
        {
            value: "Bengaluru Rural",
            en: "Bengaluru Rural",
            kn: "ಬೆಂಗಳೂರು ಗ್ರಾಮಾಂತರ",
        },
        {
            value: "Bengaluru South",
            en: "Bengaluru South",
            kn: "ಬೆಂಗಳೂರು ದಕ್ಷಿಣ",
        },
        {
            value: "Bidar",
            en: "Bidar",
            kn: "ಬೀದರ್",
        },
        {
            value: "Chamarajanagar",
            en: "Chamarajanagar",
            kn: "ಚಾಮರಾಜನಗರ",
        },
        {
            value: "Chikkaballapur",
            en: "Chikkaballapur",
            kn: "ಚಿಕ್ಕಬಳ್ಳಾಪುರ",
        },
        {
            value: "Chikkamagaluru",
            en: "Chikkamagaluru",
            kn: "ಚಿಕ್ಕಮಗಳೂರು",
        },
        {
            value: "Chitradurga",
            en: "Chitradurga",
            kn: "ಚಿತ್ರದುರ್ಗ",
        },
        {
            value: "Dakshina Kannada",
            en: "Dakshina Kannada",
            kn: "ದಕ್ಷಿಣ ಕನ್ನಡ",
        },
        {
            value: "Davangere",
            en: "Davangere",
            kn: "ದಾವಣಗೆರೆ",
        },
        {
            value: "Dharwad",
            en: "Dharwad",
            kn: "ಧಾರವಾಡ",
        },
        {
            value: "Gadag",
            en: "Gadag",
            kn: "ಗದಗ",
        },
        {
            value: "Hassan",
            en: "Hassan",
            kn: "ಹಾಸನ",
        },
        {
            value: "Haveri",
            en: "Haveri",
            kn: "ಹಾವೇರಿ",
        },
        {
            value: "Kalaburagi",
            en: "Kalaburagi",
            kn: "ಕಲಬುರಗಿ",
        },
        {
            value: "Kodagu",
            en: "Kodagu",
            kn: "ಕೊಡಗು",
        },
        {
            value: "Kolar",
            en: "Kolar",
            kn: "ಕೋಲಾರ",
        },
        {
            value: "Koppal",
            en: "Koppal",
            kn: "ಕೊಪ್ಪಳ",
        },
        {
            value: "Mandya",
            en: "Mandya",
            kn: "ಮಂಡ್ಯ",
        },
        {
            value: "Mysuru",
            en: "Mysuru",
            kn: "ಮೈಸೂರು",
        },
        {
            value: "Raichur",
            en: "Raichur",
            kn: "ರಾಯಚೂರು",
        },
        {
            value: "Shivamogga",
            en: "Shivamogga",
            kn: "ಶಿವಮೊಗ್ಗ",
        },
        {
            value: "Udupi",
            en: "Udupi",
            kn: "ಉಡುಪಿ",
        },
        {
            value: "Uttara Kannada",
            en: "Uttara Kannada",
            kn: "ಉತ್ತರ ಕನ್ನಡ",
        },
        {
            value: "Vijayanagara",
            en: "Vijayanagara",
            kn: "ವಿಜಯನಗರ",
        },
        {
            value: "Vijayapura",
            en: "Vijayapura",
            kn: "ವಿಜಯಪುರ",
        },
    ];

    /*
     * Fetch market prices
     */
    const fetchPrices = async (filters = null) => {
        setLoading(true);
        setError("");

        const selectedFilters = filters || {
            commodity,
            state,
            district,
            market,
        };

        try {
            const response = await getMarketPrices({
                commodity: selectedFilters.commodity,
                state: selectedFilters.state,
                district: selectedFilters.district,
                market: selectedFilters.market,
                limit: 100,
            });

            if (response?.success) {
                setRecords(response.records || []);
                setLastUpdated(new Date());

                if (!response.records?.length) {
                    setError(
                        isKannada
                            ? "ಆಯ್ಕೆ ಮಾಡಿದ ಪ್ರದೇಶ ಅಥವಾ ಬೆಳೆಗೆ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ."
                            : "No market price data is available for the selected location or commodity."
                    );
                }
            } else {
                setRecords([]);

                setError(
                    isKannada
                        ? "ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ."
                        : "Market price information is not available."
                );
            }
        } catch (err) {
            console.error("Market price error:", err);

            setRecords([]);

            setError(
                err?.response?.data?.detail ||
                    (isKannada
                        ? "ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಮಾಹಿತಿಯನ್ನು ಪಡೆಯಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
                        : "Unable to fetch market price information. Please try again.")
            );
        } finally {
            setLoading(false);
        }
    };

    /*
     * Initial data
     */
    useEffect(() => {
        fetchPrices();
        // Initial load only.
        // eslint-disable-next-line react-hooks/exhaustive-deps
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

        return [...new Set(districts)]
            .sort((a, b) => a.localeCompare(b))
            .map((item) => ({
                value: item,
                en: item,
                kn: item,
            }));
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

    /*
     * Format price in Indian Rupees.
     */
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

    /*
     * Reset filters.
     */
    const clearFilters = () => {
        const resetFilters = {
            commodity: "",
            state: "Karnataka",
            district: "",
            market: "",
        };

        setCommodity(resetFilters.commodity);
        setState(resetFilters.state);
        setDistrict(resetFilters.district);
        setMarket(resetFilters.market);

        /*
         * Pass reset values directly so the API doesn't
         * receive the previous React state.
         */
        fetchPrices(resetFilters);
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
                                ? "ಸರ್ಕಾರದ ಮಂಡಿ ಮಾಹಿತಿಯ ಆಧಾರದ ಮೇಲೆ ಇತ್ತೀಚಿನ ಬೆಲೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ನಿಮ್ಮ ಬೆಳೆಗೆ ಉತ್ತಮ ಮಾರುಕಟ್ಟೆಯನ್ನು ಕಂಡುಹಿಡಿಯಿರಿ."
                                : "Check the latest government mandi prices and find the best market for your crop."}
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
                                    ? "ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳನ್ನು ಹುಡುಕಿ"
                                    : "Find Market Prices"}
                            </h2>

                            <p>
                                {isKannada
                                    ? "ಬೆಳೆ ಮತ್ತು ಸ್ಥಳವನ್ನು ಆಯ್ಕೆಮಾಡಿ"
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
                                    ? "ಬೆಳೆ / ಕೃಷಿ ಉತ್ಪನ್ನ"
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
                                            key={item.value}
                                            value={item.value}
                                        >
                                            {isKannada
                                                ? item.kn
                                                : item.en}
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
                                            key={item.value}
                                            value={item.value}
                                        >
                                            {isKannada
                                                ? item.kn
                                                : item.en}
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
                                            key={item.value}
                                            value={item.value}
                                        >
                                            {isKannada
                                                ? item.kn
                                                : item.en}
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
                                    ? "ಮಾರುಕಟ್ಟೆ / ಮಂಡಿ"
                                    : "Market / Mandi"}
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
                                ? "⏳ " +
                                  (isKannada
                                      ? "ಬೆಲೆಗಳನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ..."
                                      : "Loading prices...")
                                : `🔍 ${
                                      isKannada
                                          ? "ಬೆಲೆಗಳನ್ನು ಹುಡುಕಿ"
                                          : "Search Prices"
                                  }`}
                        </button>

                        <button
                            className="market-clear-button"
                            onClick={clearFilters}
                            disabled={loading}
                        >
                            ↻{" "}
                            {isKannada
                                ? "ಫಿಲ್ಟರ್‌ಗಳನ್ನು ತೆರವುಗೊಳಿಸಿ"
                                : "Reset Filters"}
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
                                            ? "ಸರಾಸರಿ ಮಾದರಿ ಬೆಲೆ"
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
                                            ? "ಲಭ್ಯವಿರುವ ದಾಖಲೆಗಳು"
                                            : "Records Found"}
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
                                            ? "ಮಾರಾಟಕ್ಕೆ ಉತ್ತಮ ಮಾರುಕಟ್ಟೆ"
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
                                        {isKannada
                                            ? " / ಕ್ವಿಂಟಾಲ್"
                                            : " / quintal"}
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
                                            ? `${records.length} ಮಾರುಕಟ್ಟೆ ದಾಖಲೆಗಳು`
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
                                        ? "ನವೀಕರಿಸಿ"
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
                                                    ? "ಮಾರುಕಟ್ಟೆ / ಮಂಡಿ"
                                                    : "Market / Mandi"}
                                            </th>

                                            <th>
                                                {isKannada
                                                    ? "ಬೆಳೆ"
                                                    : "Commodity"}
                                            </th>

                                            <th>
                                                {isKannada
                                                    ? "ತಳಿ"
                                                    : "Variety"}
                                            </th>

                                            <th>
                                                {isKannada
                                                    ? "ಆಗಮನ ದಿನಾಂಕ"
                                                    : "Arrival Date"}
                                            </th>

                                            <th>
                                                {isKannada
                                                    ? "ಕನಿಷ್ಠ ಬೆಲೆ"
                                                    : "Min Price"}
                                            </th>

                                            <th>
                                                {isKannada
                                                    ? "ಗರಿಷ್ಠ ಬೆಲೆ"
                                                    : "Max Price"}
                                            </th>

                                            <th>
                                                {isKannada
                                                    ? "ಮಾದರಿ ಬೆಲೆ"
                                                    : "Modal Price"}
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
                                    ? "ಬೇರೆ ಬೆಳೆ ಅಥವಾ ಪ್ರದೇಶವನ್ನು ಆಯ್ಕೆಮಾಡಿ ಮತ್ತು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
                                    : "Try selecting another commodity or location."}
                            </p>

                        </div>
                    )}

                {/* Footer */}
                <div className="market-source-info">

                    <span>
                        🇮🇳{" "}

                        {isKannada
                            ? "ಸರ್ಕಾರದ ಮಂಡಿ ಬೆಲೆ ಮಾಹಿತಿ"
                            : "Government Mandi Price Information"}
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
                                ? "ಮಾಹಿತಿ ಪಡೆದ ಸಮಯ:"
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