"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WebSocketProvider = WebSocketProvider;
exports.useWebSocket = useWebSocket;
var react_1 = require("react");
var WebSocketContext = (0, react_1.createContext)(null);
function WebSocketProvider(_a) {
    var children = _a.children, url = _a.url;
    var _b = (0, react_1.useState)(false), isConnected = _b[0], setIsConnected = _b[1];
    var _c = (0, react_1.useState)(0), progress = _c[0], setProgress = _c[1];
    var _d = (0, react_1.useState)('idle'), currentStage = _d[0], setCurrentStage = _d[1];
    var _e = (0, react_1.useState)(null), error = _e[0], setError = _e[1];
    var ws = (0, react_1.useRef)(null);
    var reconnectAttempts = (0, react_1.useRef)(0);
    var maxReconnectAttempts = 5;
    var reconnectTimeout = (0, react_1.useRef)(null);
    // Clean up function to clear the reconnect timeout
    var clearReconnectTimeout = (0, react_1.useCallback)(function () {
        if (reconnectTimeout.current) {
            clearTimeout(reconnectTimeout.current);
            reconnectTimeout.current = null;
        }
    }, []);
    var handleMessage = (0, react_1.useCallback)(function (event) {
        var _a;
        try {
            var message = JSON.parse(event.data);
            switch (message.type) {
                case 'progress':
                    setProgress(Math.min(100, Math.max(0, message.data.percentage)));
                    break;
                case 'stage_update':
                    setCurrentStage(message.data.stage);
                    break;
                case 'error':
                    setError(((_a = message.data) === null || _a === void 0 ? void 0 : _a.message) || 'An error occurred');
                    break;
                case 'complete':
                    setProgress(100);
                    setCurrentStage('complete');
                    break;
                default:
                    console.warn('Unknown message type:', message.type);
            }
        }
        catch (err) {
            console.error('Error processing WebSocket message:', err);
        }
    }, []);
    var handleClose = (0, react_1.useCallback)(function () {
        setIsConnected(false);
        if (reconnectAttempts.current < maxReconnectAttempts) {
            var timeout = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000);
            reconnectTimeout.current = setTimeout(function () {
                reconnectAttempts.current += 1;
                // Reuse the existing connection logic
                if (ws.current) {
                    ws.current = new WebSocket(url);
                    setupWebSocketHandlers(ws.current);
                }
            }, timeout);
        }
        else {
            setError('Connection lost. Please refresh the page to reconnect.');
        }
    }, [url]);
    var handleError = (0, react_1.useCallback)(function (error) {
        console.error('WebSocket error:', error);
        setError('Connection error. Attempting to reconnect...');
    }, []);
    var setupWebSocketHandlers = (0, react_1.useCallback)(function (socket) {
        socket.onopen = function () {
            console.log('WebSocket connected');
            setIsConnected(true);
            reconnectAttempts.current = 0;
            setError(null);
        };
        socket.onmessage = handleMessage;
        socket.onclose = handleClose;
        socket.onerror = handleError;
    }, [handleMessage, handleClose, handleError]);
    var connect = (0, react_1.useCallback)(function () {
        // Clear any existing reconnect timeout
        clearReconnectTimeout();
        // Close existing connection if any
        if (ws.current) {
            ws.current.close();
        }
        // Create new WebSocket connection
        var socket = new WebSocket(url);
        ws.current = socket;
        setupWebSocketHandlers(socket);
        return function () {
            if (reconnectTimeout.current) {
                clearTimeout(reconnectTimeout.current);
            }
            if (socket.readyState === WebSocket.OPEN) {
                socket.close();
            }
        };
    }, [url, clearReconnectTimeout, setupWebSocketHandlers]);
    // Initialize WebSocket connection on mount
    (0, react_1.useEffect)(function () {
        connect();
        // Cleanup on unmount
        return function () {
            if (ws.current) {
                ws.current.close();
                ws.current = null;
            }
            clearReconnectTimeout();
        };
    }, [connect, clearReconnectTimeout]);
    var sendMessage = (0, react_1.useCallback)(function (message) {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            try {
                ws.current.send(JSON.stringify(message));
                return true;
            }
            catch (err) {
                console.error('Failed to send WebSocket message:', err);
                return false;
            }
        }
        return false;
    }, []);
    var contextValue = {
        isConnected: isConnected,
        progress: progress,
        currentStage: currentStage,
        error: error,
        sendMessage: sendMessage,
    };
    return (<WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>);
}
function useWebSocket() {
    var context = (0, react_1.useContext)(WebSocketContext);
    if (!context) {
        throw new Error('useWebSocket must be used within a WebSocketProvider');
    }
    return context;
}
//# sourceMappingURL=websocket.jsx.map