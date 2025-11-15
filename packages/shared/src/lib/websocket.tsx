import { createContext, useContext, useEffect, useRef, useState, useCallback, ReactNode } from 'react';

type WebSocketMessage = {
  type: 'progress' | 'stage_update' | 'error' | 'complete';
  data: any;
};

type WebSocketContextType = {
  isConnected: boolean;
  progress: number;
  currentStage: string;
  error: string | null;
  sendMessage: (message: any) => boolean;
};

const WebSocketContext = createContext<WebSocketContextType | null>(null);

type WebSocketProviderProps = {
  children: ReactNode;
  url: string;
};

export function WebSocketProvider({ children, url }: WebSocketProviderProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState('idle');
  const [error, setError] = useState<string | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  // Clean up function to clear the reconnect timeout
  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = null;
    }
  }, []);

  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      switch (message.type) {
        case 'progress':
          setProgress(Math.min(100, Math.max(0, message.data.percentage)));
          break;
        case 'stage_update':
          setCurrentStage(message.data.stage);
          break;
        case 'error':
          setError(message.data?.message || 'An error occurred');
          break;
        case 'complete':
          setProgress(100);
          setCurrentStage('complete');
          break;
        default:
          console.warn('Unknown message type:', message.type);
      }
    } catch (err) {
      console.error('Error processing WebSocket message:', err);
    }
  }, []);

  const handleClose = useCallback(() => {
    setIsConnected(false);
    
    if (reconnectAttempts.current < maxReconnectAttempts) {
      const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000);
      reconnectTimeout.current = setTimeout(() => {
        reconnectAttempts.current += 1;
        // Reuse the existing connection logic
        if (ws.current) {
          ws.current = new WebSocket(url);
          setupWebSocketHandlers(ws.current);
        }
      }, timeout);
    } else {
      setError('Connection lost. Please refresh the page to reconnect.');
    }
  }, [url]);

  const handleError = useCallback((error: Event) => {
    console.error('WebSocket error:', error);
    setError('Connection error. Attempting to reconnect...');  
  }, []);

  const setupWebSocketHandlers = useCallback((socket: WebSocket) => {
    socket.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      reconnectAttempts.current = 0;
      setError(null);
    };

    socket.onmessage = handleMessage;
    socket.onclose = handleClose;
    socket.onerror = handleError;
  }, [handleMessage, handleClose, handleError]);

  const connect = useCallback(() => {
    // Clear any existing reconnect timeout
    clearReconnectTimeout();
    
    // Close existing connection if any
    if (ws.current) {
      ws.current.close();
    }

    // Create new WebSocket connection
    const socket = new WebSocket(url);
    ws.current = socket;
    setupWebSocketHandlers(socket);

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, [url, clearReconnectTimeout, setupWebSocketHandlers]);

  // Initialize WebSocket connection on mount
  useEffect(() => {
    connect();
    
    // Cleanup on unmount
    return () => {
      if (ws.current) {
        ws.current.close();
        ws.current = null;
      }
      clearReconnectTimeout();
    };
  }, [connect, clearReconnectTimeout]);

  const sendMessage = useCallback((message: unknown): boolean => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      try {
        ws.current.send(JSON.stringify(message));
        return true;
      } catch (err) {
        console.error('Failed to send WebSocket message:', err);
        return false;
      }
    }
    return false;
  }, []);

  const contextValue = {
    isConnected,
    progress,
    currentStage,
    error,
    sendMessage,
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket(): WebSocketContextType {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
}
