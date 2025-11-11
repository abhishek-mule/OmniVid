'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Navbar } from '@/components/navbar';
import { Footer } from '@/components/footer';
import BackendPipeline from '@/components/video-gen/BackendPipeline';
import PromptInput from '@/components/video-gen/PromptInput';
import SettingsPanel from '@/components/video-gen/SettingsPanel';
import ProgressVisualization from '@/components/video-gen/ProgressVisualization';
import ResultDisplay from '@/components/video-gen/ResultDisplay';
import { Button } from '@/components/ui/button';
import { Sparkles, AlertCircle } from 'lucide-react';
import { videoApi, VideoCreateRequest } from '@omnivid/shared/lib';
import { useVideoWebSocket } from '@/hooks/useVideoWebSocket';
import { useToast } from '@omnivid/shared/hooks';

export default function GeneratePage() {
  const [prompt, setPrompt] = useState('');
  const [settings, setSettings] = useState({
    resolution: '1080p' as '720p' | '1080p' | '2k' | '4k',
    fps: 30 as 24 | 30 | 60,
    duration: 15,
    quality: 'balanced' as 'fast' | 'balanced' | 'best'
  });
  const [videoId, setVideoId] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { toast } = useToast();
  
  // WebSocket connection for real-time progress
  const {
    isConnected,
    progress,
    stage,
    status,
    outputUrl,
    error: wsError
  } = useVideoWebSocket(videoId);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a video description',
        variant: 'destructive'
      });
      return;
    }

    setIsGenerating(true);
    setError(null);
    setVideoId(null);

    try {
      // Create video generation request
      const requestData: VideoCreateRequest = {
        prompt: prompt.trim(),
        resolution: settings.resolution,
        fps: settings.fps,
        duration: settings.duration,
        quality: settings.quality,
        render_engine: 'remotion'
      };

      const response = await videoApi.createVideo(requestData);
      
      console.log('Video creation started:', response);
      setVideoId(response.id);
      
      toast({
        title: 'Success!',
        description: 'Video generation started. Watch the progress below.',
      });
      
    } catch (err: any) {
      console.error('Error creating video:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to start video generation');
      setIsGenerating(false);
      
      toast({
        title: 'Error',
        description: 'Failed to start video generation. Please try again.',
        variant: 'destructive'
      });
    }
  };

  // Update isGenerating based on status
  const isProcessing = status !== 'success' && status !== 'failed' && isGenerating;
  const hasCompleted = status === 'success';
  const hasFailed = status === 'failed' || !!wsError;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12 mt-20"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 mb-4 text-sm rounded-full bg-primary/10 border border-primary/20">
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="font-medium">AI-Powered Video Generation</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Create Your Video
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Transform your ideas into professional videos with our advanced AI pipeline
          </p>
        </motion.div>

        {/* Backend Pipeline Visualization */}
        <BackendPipeline />

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-12">
          {/* Left Column - Input & Settings */}
          <div className="lg:col-span-2 space-y-6">
            <PromptInput 
              value={prompt}
              onChange={setPrompt}
              disabled={isProcessing}
            />
            
            <SettingsPanel
              settings={settings}
              onChange={setSettings}
              disabled={isProcessing}
            />

            {/* Error Display */}
            {(error || hasFailed) && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-lg border border-red-500/50 bg-red-500/10 p-4"
              >
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-red-500 mb-1">Generation Failed</h3>
                    <p className="text-sm text-red-500/80">{error || wsError || 'An error occurred during video generation'}</p>
                    <Button
                      variant="outline"
                      size="sm"
                      className="mt-3"
                      onClick={() => {
                        setError(null);
                        setIsGenerating(false);
                        setVideoId(null);
                      }}
                    >
                      Try Again
                    </Button>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Generate Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Button
                size="lg"
                className="w-full h-14 text-lg font-semibold"
                onClick={handleGenerate}
                disabled={isProcessing || !prompt.trim()}
              >
                {isProcessing ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                    Generating... {Math.round(progress)}%
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 mr-2" />
                    Generate Video
                  </>
                )}
              </Button>

              {/* WebSocket Connection Status */}
              {videoId && (
                <div className="mt-2 text-center text-xs text-muted-foreground">
                  {isConnected ? (
                    <span className="flex items-center justify-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                      Connected to server
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-orange-500 animate-pulse" />
                      Connecting...
                    </span>
                  )}
                </div>
              )}
            </motion.div>
          </div>

          {/* Right Column - Progress & Result */}
          <div className="space-y-6">
            {isProcessing && videoId && (
              <ProgressVisualization
                progress={progress}
                currentStage={stage || 'Initializing'}
              />
            )}

            {hasCompleted && outputUrl && videoId && (
              <ResultDisplay videoUrl={videoApi.getDownloadUrl(videoId)} />
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
