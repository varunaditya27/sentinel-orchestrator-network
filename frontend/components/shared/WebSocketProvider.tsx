"use client";

import React, { createContext, useContext, useEffect, useRef, useState, ReactNode } from "react";

interface WebSocketContextType {
    isConnected: boolean;
    sendMessage: (message: any) => void;
    subscribe: (callback: (message: any) => void) => () => void;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

interface WebSocketProviderProps {
    children: ReactNode;
    url?: string;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({
    children,
    url = "ws://localhost:8000/ws/logs"
}) => {
    const [isConnected, setIsConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);
    const subscribersRef = useRef<Set<(message: any) => void>>(new Set());

    useEffect(() => {
        const connect = () => {
            try {
                const ws = new WebSocket(url);
                wsRef.current = ws;

                ws.onopen = () => {
                    setIsConnected(true);
                    console.log("WebSocket connected");
                };

                ws.onmessage = (event) => {
                    try {
                        const message = JSON.parse(event.data);
                        // Notify all subscribers
                        subscribersRef.current.forEach(callback => callback(message));
                    } catch (error) {
                        console.error("Failed to parse WebSocket message:", error);
                    }
                };

                ws.onclose = () => {
                    setIsConnected(false);
                    console.log("WebSocket disconnected");
                    // Attempt to reconnect after 5 seconds
                    setTimeout(connect, 5000);
                };

                ws.onerror = (error) => {
                    console.error("WebSocket error:", error);
                    setIsConnected(false);
                };
            } catch (error) {
                console.error("Failed to create WebSocket connection:", error);
                setTimeout(connect, 5000);
            }
        };

        connect();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [url]);

    const sendMessage = (message: any) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message));
        } else {
            console.warn("WebSocket is not connected");
        }
    };

    const subscribe = (callback: (message: any) => void) => {
        subscribersRef.current.add(callback);
        return () => {
            subscribersRef.current.delete(callback);
        };
    };

    const value: WebSocketContextType = {
        isConnected,
        sendMessage,
        subscribe
    };

    return (
        <WebSocketContext.Provider value={value}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocket = (): WebSocketContextType => {
    const context = useContext(WebSocketContext);
    if (!context) {
        throw new Error("useWebSocket must be used within a WebSocketProvider");
    }
    return context;
};
