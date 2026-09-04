import { useEffect, useState } from "react";

import {
    getUnreadNotifications,
    markNotificationAsRead,
    markAllNotificationsAsRead
} from "../services/api";

import "./NotificationBell.css";


function NotificationBell() {

    const [
        notifications,
        setNotifications
    ] = useState([]);

    const [
        open,
        setOpen
    ] = useState(false);


    // =====================================================
    // LOAD NOTIFICATIONS
    // =====================================================

    const loadNotifications = async () => {

        try {

            const data =
                await getUnreadNotifications();


            /*
             * Support both:
             *
             * [
             *   {...},
             *   {...}
             * ]
             *
             * and:
             *
             * {
             *   data: [...]
             * }
             */

            const notificationData =
                Array.isArray(data)
                    ? data
                    : Array.isArray(data?.data)
                        ? data.data
                        : [];


            setNotifications(
                notificationData
            );

        }

        catch (error) {

            console.error(
                "Notification error:",
                error
            );

        }

    };


    // =====================================================
    // INITIAL LOAD + PERIODIC REFRESH
    // =====================================================

    useEffect(() => {

        loadNotifications();


        /*
         * Refresh every 15 seconds.
         */

        const interval =
            setInterval(
                loadNotifications,
                15000
            );


        return () => {

            clearInterval(interval);

        };

    }, []);


    // =====================================================
    // MARK SINGLE NOTIFICATION AS READ
    // =====================================================

    const handleRead = async (
        notificationId
    ) => {

        try {

            await markNotificationAsRead(
                notificationId
            );


            /*
             * Remove immediately from UI.
             */

            setNotifications(
                previous =>
                    previous.filter(
                        notification =>
                            notification.id !==
                            notificationId
                    )
            );

        }

        catch (error) {

            console.error(
                "Unable to mark notification:",
                error
            );

        }

    };


    // =====================================================
    // MARK ALL NOTIFICATIONS AS READ
    // =====================================================

    const handleMarkAllRead = async () => {

        try {

            await markAllNotificationsAsRead();

            setNotifications([]);

        }

        catch (error) {

            console.error(
                "Unable to mark notifications:",
                error
            );

        }

    };


    // =====================================================
    // TOGGLE NOTIFICATION PANEL
    // =====================================================

    const toggleNotifications = () => {

        setOpen(
            previous =>
                !previous
        );

    };


    // =====================================================
    // UI
    // =====================================================

    return (

        <div className="notification-container">


            {/* =================================================
                NOTIFICATION BUTTON
            ================================================= */}

            <button

                className="notification-button"

                onClick={
                    toggleNotifications
                }

                aria-label="Notifications"

                title="Notifications"

            >

                <span className="notification-bell-icon">

                    🔔

                </span>


                {/* =================================================
                    UNREAD COUNT
                ================================================= */}

                {notifications.length > 0 && (

                    <span className="notification-count">

                        {notifications.length > 99
                            ? "99+"
                            : notifications.length}

                    </span>

                )}

            </button>


            {/* =================================================
                NOTIFICATION PANEL
            ================================================= */}

            {open && (

                <div className="notification-panel">


                    {/* =================================================
                        HEADER
                    ================================================= */}

                    <div className="notification-header">

                        <div>

                            <h3>

                                Notifications

                            </h3>

                            {notifications.length > 0 && (

                                <span className="notification-subtitle">

                                    {notifications.length} unread

                                </span>

                            )}

                        </div>


                        {notifications.length > 0 && (

                            <button

                                className="mark-all-button"

                                onClick={
                                    handleMarkAllRead
                                }

                            >

                                Mark all read

                            </button>

                        )}

                    </div>


                    {/* =================================================
                        NO NOTIFICATIONS
                    ================================================= */}

                    {notifications.length === 0 ? (

                        <div className="no-notifications">

                            <div className="no-notification-icon">

                                🔔

                            </div>


                            <h4>

                                No new notifications

                            </h4>


                            <p>

                                You're all caught up!

                            </p>

                        </div>

                    ) : (


                        /* =================================================
                           NOTIFICATION LIST
                        ================================================= */

                        <div className="notification-list">

                            {notifications.map(
                                notification => (

                                    <div

                                        key={
                                            notification.id
                                        }

                                        className="notification-item"

                                    >

                                        <div className="notification-content">


                                            {/* =================================================
                                                TITLE
                                            ================================================= */}

                                            <strong>

                                                {
                                                    notification.title ||
                                                    "Notification"
                                                }

                                            </strong>


                                            {/* =================================================
                                                MESSAGE
                                            ================================================= */}

                                            <p>

                                                {
                                                    notification.message ||
                                                    ""
                                                }

                                            </p>


                                            {/* =================================================
                                                CREATED TIME
                                            ================================================= */}

                                            {notification.created_at && (

                                                <small>

                                                    {new Date(
                                                        notification.created_at
                                                    ).toLocaleString()}

                                                </small>

                                            )}

                                        </div>


                                        {/* =================================================
                                            MARK READ
                                        ================================================= */}

                                        <button

                                            className="notification-read-button"

                                            onClick={() =>
                                                handleRead(
                                                    notification.id
                                                )
                                            }

                                            aria-label="Mark notification as read"

                                            title="Mark as read"

                                        >

                                            ✓

                                        </button>

                                    </div>

                                )
                            )}

                        </div>

                    )}

                </div>

            )}

        </div>

    );

}


export default NotificationBell;