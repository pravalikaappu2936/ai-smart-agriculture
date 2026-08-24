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

            setNotifications(data);

        } catch (error) {

            console.error(
                "Notification error:",
                error
            );
        }
    };


    // =====================================================
    // INITIAL LOAD + REFRESH
    // =====================================================

    useEffect(() => {

        loadNotifications();

        const interval =
            setInterval(
                loadNotifications,
                5000
            );

        return () => {

            clearInterval(interval);

        };

    }, []);


    // =====================================================
    // MARK AS READ
    // =====================================================

    const handleRead = async (
        notificationId
    ) => {

        try {

            await markNotificationAsRead(
                notificationId
            );

            setNotifications(
                previous =>
                    previous.filter(
                        notification =>
                            notification.id !==
                            notificationId
                    )
            );

        } catch (error) {

            console.error(
                "Unable to mark notification:",
                error
            );
        }
    };


    // =====================================================
    // MARK ALL READ
    // =====================================================

    const handleMarkAllRead = async () => {

        try {

            await markAllNotificationsAsRead();

            setNotifications([]);

        } catch (error) {

            console.error(
                "Unable to mark notifications:",
                error
            );
        }
    };


    return (

        <div className="notification-container">

            <button
                className="notification-button"
                onClick={() =>
                    setOpen(
                        previous =>
                            !previous
                    )
                }
            >

                🔔

                {notifications.length > 0 && (

                    <span className="notification-count">

                        {notifications.length}

                    </span>

                )}

            </button>


            {open && (

                <div className="notification-panel">

                    <div className="notification-header">

                        <h3>
                            Notifications
                        </h3>

                        {notifications.length > 0 && (

                            <button
                                onClick={
                                    handleMarkAllRead
                                }
                            >
                                Mark all read
                            </button>

                        )}

                    </div>


                    {notifications.length === 0 ? (

                        <div className="no-notifications">

                            <span>
                                🔔
                            </span>

                            <p>
                                No new notifications
                            </p>

                        </div>

                    ) : (

                        <div className="notification-list">

                            {notifications.map(
                                notification => (

                                    <div
                                        key={
                                            notification.id
                                        }
                                        className="notification-item"
                                    >

                                        <div>

                                            <strong>
                                                {
                                                    notification.title
                                                }
                                            </strong>

                                            <p>
                                                {
                                                    notification.message
                                                }
                                            </p>

                                            <small>
                                                {
                                                    new Date(
                                                        notification.created_at
                                                    ).toLocaleString()
                                                }
                                            </small>

                                        </div>


                                        <button
                                            onClick={() =>
                                                handleRead(
                                                    notification.id
                                                )
                                            }
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