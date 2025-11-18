'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import BackendPipeline from '@/components/video-gen/BackendPipeline';
import PromptInput from '@/components/video-gen/PromptInput';
import SettingsPanel from '@/components/video-gen/SettingsPanel';
import ResultDisplay from '@/components/video-gen/ResultDisplay';
import { Sparkles, Zap, AlertCircle } from "lucide-react";
import { useAuth } from "@omnivid/shared/contexts/AuthContext";
import { videoApi } from "@omnivid/shared/lib/auth";
import { useWebSocket } from "@omnivid/shared/hooks/useWebSocket";

interface Settings {
  resolution: '720p' | '1080p' | '2k' | '4k';
  fps: 24 | 30 | 60;
  duration: number;
  quality: 'fast' | 'balanced' | 'best';
  engine: 'remotion' | 'ffmpeg' | 'blender' | 'manim';
}

export default function GeneratePage() {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [currentVideoId, setCurrentVideoId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [settings, setSettings] = useState<Settings>({
    resolution: '1080p',
    fps: 30,
    duration: 30,
    quality: 'balanced',
    engine: 'remotion'
  });

  const router = useRouter();
  const { user, token } = useAuth();

  // WebSocket for real-time progress updates
  const wsUrl = currentVideoId ? `ws://localhost:8000/ws/videos/${currentVideoId}` : null;
  const { messages, isConnected } = useWebSocket(wsUrl || '');

  // Redirect if not authenticated
  useEffect(() => {
    if (!user && !token) {
      router.push('/auth/login');
    }
  }, [user, token, router]);

  useEffect(() => {
    // Handle WebSocket messages for progress updates
    if (messages.length > 0 && currentVideoId) {
      const latestMessage = messages[messages.length - 1];
      if (latestMessage.type === 'progress') {
        // Update progress (you can extend this based on backend message structure)
        console.log('Progress update:', latestMessage.data);
      } else if (latestMessage.type === 'completed') {
        setIsGenerating(false);
        setResult({ status: 'completed', videoId: currentVideoId });
      } else if (latestMessage.type === 'error') {
        setIsGenerating(false);
        setError(latestMessage.data || 'Video generation failed');
      }
    }
  }, [messages, currentVideoId]);

  const handleGenerate = async () => {
    if (!prompt.trim() || !token) return;

    setError(null);
    setIsGenerating(true);
    setResult(null);

    try {
      // Create video through API
      const videoData = {
        title: prompt.slice(0, 100), // Use first 100 chars as title
        description: prompt,
        engine: settings.engine,
        settings: {
          resolution: settings.resolution,
          fps: settings.fps,
          duration: settings.duration,
          quality: settings.quality,
        },
        prompt: prompt,
      };

      const response = await videoApi.createVideo(token, videoData);
      const videoId = response.id;
      setCurrentVideoId(videoId);

      // Video creation successful, waiting for WebSocket updates
      console.log('Video created with ID:', videoId);

    } catch (err) {
      setIsGenerating(false);
      setError(err instanceof Error ? err.message : 'Failed to start video generation');
    }
  };

  return (
    <div className="min-h-screen gradient-bg">
      <div className="container py-10">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12 animate-fade-in">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 mb-6">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl md:text-6xl font-bold mb-4 text-gradient">
              Generate Your Video
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Transform your ideas into stunning videos with our advanced AI generation technology.
            </p>
          </div>

          <BackendPipeline />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-primary" />
                  Generation Settings
                </CardTitle>
                <CardDescription>
                  Configure your video generation parameters
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {error && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-red-700">{error}</AlertDescription>
                  </Alert>
                )}

                <PromptInput
                  value={prompt}
                  onChange={setPrompt}
                  disabled={isGenerating}
                />
                <SettingsPanel
                  settings={settings}
                  onChange={setSettings}
                  disabled={isGenerating}
                />
                <Button
                  onClick={handleGenerate}
                  disabled={!prompt.trim() || isGenerating}
                  className="w-full h-12 gradient-primary text-white hover:opacity-90"
                  size="lg"
                >
                  {isGenerating ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Generating Video... {isConnected ? '(Real-time updates active)' : ''}
                    </>
                  ) : (
                    'Generate Video'
                  )}
                </Button>
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Preview & Results</CardTitle>
                <CardDescription>Watch your generated video here</CardDescription>
              </CardHeader>
              <CardContent>
                <ResultDisplay result={result} isLoading={isGenerating} />
              </CardContent>
            </Card>
          </div>

          {/* Recent Generations */}
          <Card className="glass-card mt-12">
            <CardHeader>
              <CardTitle>Recent Generations</CardTitle>
              <CardDescription>Your previously generated videos</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="glass p-4 rounded-lg hover:scale-105 transition-transform cursor-pointer">
                    <div className="aspect-video bg-muted rounded-lg mb-3 flex items-center justify-center">
                      <span className="text-muted-foreground">Video {i}</span>
                    </div>
                    <h3 className="font-medium mb-1">Generated Video {i}</h3>
                    <p className="text-sm text-muted-foreground">2 days ago</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
