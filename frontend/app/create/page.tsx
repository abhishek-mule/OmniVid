'use client';

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import BackendPipeline from '@/components/video-gen/BackendPipeline';
import PromptInput from '@/components/video-gen/PromptInput';
import SettingsPanel from '@/components/video-gen/SettingsPanel';
import ResultDisplay from '@/components/video-gen/ResultDisplay';

export default function CreateProjectPage() {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<string | null>(null);

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
    <div className="container py-10">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">AI Video Generator</h1>
        <p className="text-muted-foreground mb-8">Create stunning videos with AI-powered generation.</p>

        <BackendPipeline />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card>
            <CardHeader>
              <CardTitle>Video Configuration</CardTitle>
              <CardDescription>Customize your video generation settings.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <PromptInput
                value={prompt}
                onChange={setPrompt}
                disabled={isGenerating}
              />
              <SettingsPanel />
              <Button
                onClick={handleGenerate}
                disabled={!prompt.trim() || isGenerating}
                className="w-full"
              >
                {isGenerating ? 'Generating...' : 'Generate Video'}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Preview & Results</CardTitle>
              <CardDescription>See your generated video here.</CardDescription>
            </CardHeader>
            <CardContent>
              <ResultDisplay result={result} isLoading={isGenerating} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
