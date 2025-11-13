import { useState, useEffect, useRef, useCallback } from 'react';
import { simpleApi } from '@omnivid/shared/lib';

type VideoStatus = 'pending' | 'parsing' | 'rendering' | 'encoding' | 'finalizing' | 'success' | 'failed';

interface WebSocketMessage {
  type: 'progress' | 'stage_update' | 'status_update' | 'error' | 'complete';
  data: any;
}

export function useVideoWebSocket(videoId: string | null) {
  const [isConnected, setIsConnected] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState<string>('');
  const [status, setStatus] = useState<VideoStatus>('pending');
  const [outputUrl, setOutputUrl] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const ws = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 3;

  const connect = useCallback(() => {
    if (!videoId) return;

    if (ws.current) {
      ws.current.close();
    }

    const url = simpleApi.getWebSocketUrl(videoId);
    const socket = new WebSocket(url);

    socket.onopen = () => {
      console.log('Video WebSocket connected');
      setIsConnected(true);
      reconnectAttempts.current = 0;
      setError(null);
    };

    socket.onmessage = (event: MessageEvent) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);

        switch (message.type) {
          case 'progress':
            setProgress(Math.min(100, Math.max(0, message.data.percentage || message.data.progress || 0)));
            break;
          case 'stage_update':
            setStage(message.data.stage || message.data.current_stage || '');
            break;
          case 'status_update':
            setStatus(message.data.status || 'pending');
            if (message.data.output_url) {
              setOutputUrl(message.data.output_url);
            }
            break;
          case 'complete':
            setProgress(100);
            setStatus('success');
            setStage('Complete');
            if (message.data.output_url) {
              setOutputUrl(message.data.output_url);
            }
            break;
          case 'error':
            setError(message.data?.message || message.data?.error || 'An error occurred');
            setStatus('failed');
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
      console.log('Video WebSocket disconnected');
    };

    socket.onerror = (error: Event) => {
      console.error('Video WebSocket error:', error);
      setError('Connection error');
    };

    ws.current = socket;
  }, [videoId]);

  useEffect(() => {
    if (videoId) {
      connect();
    }

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [videoId, connect]);

  // Reset state when videoId changes
  useEffect(() => {
    setProgress(0);
    setStage('');
    setStatus('pending');
    setOutputUrl('');
    setError(null);
    setIsConnected(false);
  }, [videoId]);

  return {
    isConnected,
    progress,
    stage,
    status,
    outputUrl,
    error,
  };
}