'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import BackendPipeline from '@/components/video-gen/BackendPipeline';
import ResultDisplay from '@/components/video-gen/ResultDisplay';
import { Sparkles, Zap, AlertCircle, Brain, Cpu, MessageSquare } from "lucide-react";
import { useSupabaseAuth } from "@/components/auth/AuthProvider";
import { aiApi, projectApi } from "@omnivid/shared/lib/auth";
import { useWebSocket } from "@omnivid/shared/hooks/useWebSocket";

export const dynamic = 'force-dynamic';

export default function GeneratePage() {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [currentVideoId, setCurrentVideoId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [aiCapabilities, setAiCapabilities] = useState<any>(null);

  const router = useRouter();
  const { user, session } = useSupabaseAuth();
  const token = session?.access_token;

  // WebSocket for real-time progress updates
  const wsUrl = currentVideoId ? `ws://localhost:8000/ws/videos/${currentVideoId}` : null;
  const { messages, isConnected } = useWebSocket(wsUrl || '');

  // Redirect if not authenticated
  useEffect(() => {
    if (!user && !token) {
      router.push('/auth/login');
    }
  }, [user, token, router]);

  // Load projects and AI capabilities on mount
  useEffect(() => {
    if (token) {
      loadProjects();
      loadAiCapabilities();
    }
  }, [token]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadProjects = async () => {
    if (!token) return;

    try {
      const projectsData = await projectApi.getProjects(token);
      setProjects(projectsData);

      // Auto-select first project
      if (projectsData.length > 0 && !selectedProjectId) {
        setSelectedProjectId(projectsData[0].id);
      }
    } catch (err) {
      console.error('Failed to load projects:', err);
    }
  };

  const loadAiCapabilities = async () => {
    if (!token) return;

    try {
      const capabilities = await aiApi.getCapabilities(token);
      setAiCapabilities(capabilities);
    } catch (err) {
      console.error('Failed to load AI capabilities:', err);
    }
  };

  // Handle WebSocket progress updates
  useEffect(() => {
    if (messages.length > 0 && currentVideoId) {
      const latestMessage = messages[messages.length - 1];
      if (latestMessage.type === 'video_progress') {
        // Update progress (you can extend this based on backend message structure)
        console.log('Progress update:', latestMessage.data);
        setResult((prev: any) => prev ? {
          ...prev,
          progress: latestMessage.data.progress,
          status: latestMessage.data.status
        } : null);
      } else if (latestMessage.type === 'video_completed') {
        setIsGenerating(false);
        setResult({ status: 'completed', videoId: currentVideoId });
      } else if (latestMessage.type === 'video_error') {
        setIsGenerating(false);
        setError(latestMessage.data || 'Video generation failed');
      }
    }
  }, [messages, currentVideoId]);

  const handleGenerate = async () => {
    if (!prompt.trim() || !token || !selectedProjectId) return;

    setError(null);
    setIsGenerating(true);
    setResult(null);

    try {
      // Generate video using AI API
      const response = await aiApi.generateVideo(
        token,
        prompt,
        selectedProjectId,
        {
          title: `AI Generated: ${prompt.slice(0, 50)}...`,
        }
      );

      const videoId = response.video_id;
      setCurrentVideoId(videoId);

      // Video creation successful, waiting for WebSocket updates
      console.log('AI video generation started with ID:', videoId);

      setResult({
        status: 'processing',
        videoId,
        progress: 0,
        message: 'AI is analyzing your prompt and generating code...'
      });

    } catch (err) {
      setIsGenerating(false);
      setError(err instanceof Error ? err.message : 'Failed to start AI video generation');
    }
  };

  return (
    <div className="min-h-screen gradient-bg">
      <div className="container py-10">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12 animate-fade-in">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 mb-6">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl md:text-6xl font-bold mb-4 text-gradient">
              OmniVid Lite
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-6">
              Transform natural language into professional motion graphics.
              AI generates code, engines render it.
            </p>

            {/* AI Capabilities Badge */}
            <div className="flex flex-wrap justify-center gap-2 mb-6">
              <Badge variant="secondary" className="flex items-center gap-1">
                <MessageSquare className="w-3 h-3" />
                Natural Language
              </Badge>
              <Badge variant="secondary" className="flex items-center gap-1">
                <Brain className="w-3 h-3" />
                AI Code Generation
              </Badge>
              <Badge variant="secondary" className="flex items-center gap-1">
                <Cpu className="w-3 h-3" />
                Multi-Engine
              </Badge>
            </div>
          </div>

          <BackendPipeline />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-primary" />
                  Describe Your Video
                </CardTitle>
                <CardDescription>
                  Tell us what you want to create. Our AI will handle the rest.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {error && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-red-700">{error}</AlertDescription>
                  </Alert>
                )}

                {/* Project Selection */}
                <div className="space-y-2">
                  <label className="text-sm font-medium">Project</label>
                  <select
                    value={selectedProjectId || ''}
                    onChange={(e) => setSelectedProjectId(parseInt(e.target.value))}
                    className="w-full px-3 py-2 border rounded-md bg-background"
                    disabled={isGenerating}
                  >
                    <option value="">Select a project...</option>
                    {projects.map((project) => (
                      <option key={project.id} value={project.id}>
                        {project.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Natural Language Prompt */}
                <div className="space-y-2">
                  <label className="text-sm font-medium">What do you want to create?</label>
                  <Textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="e.g., 'Create a smooth animated text introducing our new product with a blue gradient background'"
                    className="min-h-[120px] resize-none"
                    disabled={isGenerating}
                  />
                  <p className="text-xs text-muted-foreground">
                    Be descriptive! Include colors, style preferences, duration, and any specific animations.
                  </p>
                </div>

                <Button
                  onClick={handleGenerate}
                  disabled={!prompt.trim() || !selectedProjectId || isGenerating}
                  className="w-full h-12 gradient-primary text-white hover:opacity-90"
                  size="lg"
                >
                  {isGenerating ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      AI Generating... {isConnected ? '(Real-time updates active)' : ''}
                    </>
                  ) : (
                    <>Generate with AI</>
                  )}
                </Button>
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardHeader>
                <CardTitle>AI Generation Progress</CardTitle>
                <CardDescription>Watch your video come to life through AI</CardDescription>
              </CardHeader>
              <CardContent>
                <ResultDisplay result={result} isLoading={isGenerating} />
              </CardContent>
            </Card>
          </div>

          {/* AI Capabilities Info */}
          {aiCapabilities && (
            <Card className="glass-card mt-12">
              <CardHeader>
                <CardTitle>AI Capabilities</CardTitle>
                <CardDescription>Powered by intelligent video generation</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <Badge variant="outline" className="mb-2">Engines</Badge>
                    <p className="text-sm text-muted-foreground">
                      {aiCapabilities.supported_engines?.join(', ') || 'Remotion, Manim, FFmpeg'}
                    </p>
                  </div>
                  <div className="text-center">
                    <Badge variant="outline" className="mb-2">Scenes</Badge>
                    <p className="text-sm text-muted-foreground">
                      {aiCapabilities.supported_scenes?.join(', ') || 'Text, Math, Animation'}
                    </p>
                  </div>
                  <div className="text-center">
                    <Badge variant="outline" className="mb-2">Resolution</Badge>
                    <p className="text-sm text-muted-foreground">
                      Up to {aiCapabilities.supported_resolutions?.[1] || '4K'}
                    </p>
                  </div>
                  <div className="text-center">
                    <Badge variant="outline" className="mb-2">Generation</Badge>
                    <p className="text-sm text-muted-foreground">
                      {aiCapabilities.estimated_generation_time || '10-60 seconds'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
