'use client';

import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Zap, Send, Wifi, WifiOff } from "lucide-react";

export default function WebSocketTestPage() {
  const [messages, setMessages] = useState<string[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);

  const addMessage = (message: string) => {
    setMessages(prev => [...prev.slice(-9), message]); // Keep last 10 messages
  };

  const handleConnect = () => {
    setIsConnected(true);
    addMessage('Connected to WebSocket server');
  };

  const handleDisconnect = () => {
    setIsConnected(false);
    addMessage('Disconnected from WebSocket server');
  };

  const handleSend = () => {
    if (inputMessage.trim()) {
      addMessage(`Sent: ${inputMessage}`);
      setInputMessage('');
    }
  };

  // Simulate receiving messages
  useEffect(() => {
    if (isConnected) {
      const interval = setInterval(() => {
        const mockMessages = [
          'Video generation started',
          'Processing frame 1/100',
          'AI model loaded successfully',
          'Rendering completed',
          'Export ready for download'
        ];
        const randomMessage = mockMessages[Math.floor(Math.random() * mockMessages.length)];
        addMessage(`Received: ${randomMessage}`);
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [isConnected]);

  return (
    <div className="min-h-screen gradient-bg">
      <div className="container py-10">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8 animate-fade-in">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 mb-6">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold mb-4 text-gradient">WebSocket Test</h1>
            <p className="text-muted-foreground">
              Test real-time communication for video generation updates
            </p>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            {/* Connection Controls */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {isConnected ? <Wifi className="w-5 h-5 text-green-500" /> : <WifiOff className="w-5 h-5 text-red-500" />}
                  Connection Status
                </CardTitle>
                <CardDescription>
                  Manage WebSocket connection
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-4">
                  <Badge variant={isConnected ? "default" : "secondary"}>
                    {isConnected ? "Connected" : "Disconnected"}
                  </Badge>
                </div>

                <div className="flex gap-2">
                  {!isConnected ? (
                    <Button onClick={handleConnect} className="flex-1 gradient-primary text-white">
                      Connect
                    </Button>
                  ) : (
                    <Button onClick={handleDisconnect} variant="destructive" className="flex-1">
                      Disconnect
                    </Button>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Send Message</label>
                  <div className="flex gap-2">
                    <Input
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      placeholder="Type a message..."
                      onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    />
                    <Button onClick={handleSend} disabled={!isConnected}>
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Message Log */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Message Log</CardTitle>
                <CardDescription>
                  Real-time WebSocket messages
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80 overflow-y-auto space-y-2 p-2 bg-muted/30 rounded-lg">
                  {messages.length === 0 ? (
                    <p className="text-muted-foreground text-center py-8">
                      No messages yet. Connect to start receiving updates.
                    </p>
                  ) : (
                    messages.map((message, index) => (
                      <div
                        key={index}
                        className="p-2 bg-background/50 rounded text-sm animate-fade-in"
                      >
                        <span className="text-muted-foreground text-xs">
                          {new Date().toLocaleTimeString()}
                        </span>
                        <p>{message}</p>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Info Card */}
          <Card className="glass-card mt-8">
            <CardHeader>
              <CardTitle>About WebSocket Testing</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                This page simulates WebSocket connections for real-time video generation updates.
                In a production environment, this would connect to your backend WebSocket server
                to receive live updates on video processing status, progress, and completion notifications.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}