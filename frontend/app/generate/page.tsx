'use client';

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import BackendPipeline from '@/components/video-gen/BackendPipeline';
import PromptInput from '@/components/video-gen/PromptInput';
import SettingsPanel from '@/components/video-gen/SettingsPanel';
import ResultDisplay from '@/components/video-gen/ResultDisplay';
import { Sparkles, Zap } from "lucide-react";

interface Settings {
  resolution: '720p' | '1080p' | '2k' | '4k';
  fps: 24 | 30 | 60;
  duration: number;
  quality: 'fast' | 'balanced' | 'best';
}

export default function GeneratePage() {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [settings, setSettings] = useState<Settings>({
    resolution: '1080p',
    fps: 30,
    duration: 30,
    quality: 'balanced'
  });

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    // Simulate API call
    setTimeout(() => {
      setResult('Video generated successfully!');
      setIsGenerating(false);
    }, 3000);
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
                  {isGenerating ? 'Generating...' : 'Generate Video'}
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