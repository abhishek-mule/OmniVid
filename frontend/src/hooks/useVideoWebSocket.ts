import { useEffect, useRef, useState, useCallback } from 'react';

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
const API_V1_PREFIX = '/api/v1';

export interface VideoProgressMessage {
  video_id: string;
  progress: number;
  stage: string;
  status: 'pending' | 'parsing' | 'rendering' | 'encoding' | 'finalizing' | 'success' | 'failed';
  output_url?: string;
  error?: string;
  timestamp: string;
}

export interface UseVideoWebSocketReturn {
  isConnected: boolean;
  progress: number;
  stage: string;
  status: string;
  outputUrl?: string;
  error?: string;
  lastMessage?: VideoProgressMessage;
  reconnect: () => void;
}

export function useVideoWebSocket(videoId: string | null): UseVideoWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState('');
  const [status, setStatus] = useState('pending');
  const [outputUrl, setOutputUrl] = useState<string>();
  const [error, setError] = useState<string>();
  const [lastMessage, setLastMessage] = useState<VideoProgressMessage>();
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (!videoId) return;

    try {
      const wsUrl = `${WS_BASE_URL}${API_V1_PREFIX}/ws/videos/${videoId}`;
      console.log('Connecting to WebSocket:', wsUrl);
      
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected for video:', videoId);
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        
        // Send ping every 30 seconds to keep connection alive
        const pingInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
          }
        }, 30000);

        ws.addEventListener('close', () => {
          clearInterval(pingInterval);
        });
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket message:', data);

          // Handle different message types
          if (data.type === 'connection') {
            console.log('Connection confirmed:', data.message);
            return;
          }

          if (data.type === 'pong') {
            return;
          }

          // Update state from progress message
          if (data.video_id === videoId) {
            setLastMessage(data);
            
            if (data.progress !== undefined) {
              setProgress(data.progress);
            }
            
            if (data.stage) {
              setStage(data.stage);
            }
            
            if (data.status) {
              setStatus(data.status);
            }
            
            if (data.output_url) {
              setOutputUrl(data.output_url);
            }
            
            if (data.error) {
              setError(data.error);
            }
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        wsRef.current = null;

        // Attempt to reconnect if not a normal closure
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);
          
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };
    } catch (err) {
      console.error('Error creating WebSocket:', err);
      setError('Failed to create WebSocket connection');
    }
  }, [videoId]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Component unmounted');
      wsRef.current = null;
    }

    setIsConnected(false);
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    connect();
  }, [connect, disconnect]);

  // Connect on mount or when videoId changes
  useEffect(() => {
    if (videoId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [videoId, connect, disconnect]);

  return {
    isConnected,
    progress,
    stage,
    status,
    outputUrl,
    error,
    lastMessage,
    reconnect,
  };
}
