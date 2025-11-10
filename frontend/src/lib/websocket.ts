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
  const reconnectTimeout = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    if (ws.current) {
      ws.current.close();
    }

    const socket = new WebSocket(url);
    
    socket.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      reconnectAttempts.current = 0;
      setError(null);
    };

    socket.onmessage = (event: MessageEvent) => {
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
    };

    socket.onclose = () => {
      setIsConnected(false);
      
      if (reconnectAttempts.current < maxReconnectAttempts) {
        const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000);
        reconnectTimeout.current = setTimeout(() => {
          reconnectAttempts.current += 1;
          connect();
        }, timeout);
      } else {
        setError('Connection lost. Please refresh the page to reconnect.');
      }
    };

    socket.onerror = (error: Event) => {
      console.error('WebSocket error:', error);
      setError('Connection error. Attempting to reconnect...');
    };

    ws.current = socket;

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, [url]);

  useEffect(() => {
    connect();
    
    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, [connect]);

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
