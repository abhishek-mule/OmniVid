'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  Sparkles, 
  Wand2, 
  Settings, 
  Layers, 
  Download,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react';
import { PromptEditor } from './PromptEditor';
import { VideoControls } from './VideoControls';
import { TemplateSelector } from './TemplateSelector';
import { ProgressTracker } from './ProgressTracker';
import { VideoPreview } from './VideoPreview';

interface VideoSettings {
  resolution: '720p' | '1080p' | '2k' | '4k';
  fps: 24 | 30 | 60;
  duration: number;
  quality: 'fast' | 'balanced' | 'best';
  template?: string;
}

export function VideoGeneratorStudio() {
  const [prompt, setPrompt] = useState('');
  const [settings, setSettings] = useState<VideoSettings>({
    resolution: '1080p',
    fps: 30,
    duration: 15,
    quality: 'balanced',
  });
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState('');
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setProgress(0);
    // Simulation - replace with actual API call
    const stages = [
      'Analyzing prompt...',
      'Generating script...',
      'Creating scenes...',
      'Rendering video...',
      'Finalizing...'
    ];
    
    for (let i = 0; i < stages.length; i++) {
      setCurrentStage(stages[i]);
      await new Promise(resolve => setTimeout(resolve, 2000));
      setProgress((i + 1) * 20);
    }
    
    setIsGenerating(false);
    setVideoUrl('/placeholder-video.mp4');
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-violet-600 to-fuchsia-600 bg-clip-text text-transparent">
                Video Studio
              </h1>
              <p className="text-muted-foreground mt-2">
                Create stunning videos with AI-powered generation
              </p>
            </div>
            <Badge variant="secondary" className="text-sm">
              <Sparkles className="w-3 h-3 mr-1" />
              Pro Features
            </Badge>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel - Input & Controls */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="lg:col-span-2 space-y-6"
          >
            {/* Prompt Editor */}
            <div className="rounded-2xl border border-border bg-card p-6 backdrop-blur-sm">
              <div className="flex items-center gap-2 mb-4">
                <Wand2 className="w-5 h-5 text-primary" />
                <h2 className="text-xl font-semibold">Describe Your Video</h2>
              </div>
              <PromptEditor value={prompt} onChange={setPrompt} />
            </div>

            {/* Tabs for Templates and Settings */}
            <Tabs defaultValue="settings" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="settings" className="flex items-center gap-2">
                  <Settings className="w-4 h-4" />
                  Settings
                </TabsTrigger>
                <TabsTrigger value="templates" className="flex items-center gap-2">
                  <Layers className="w-4 h-4" />
                  Templates
                </TabsTrigger>
              </TabsList>

              <TabsContent value="settings" className="mt-6">
                <div className="rounded-2xl border border-border bg-card p-6 backdrop-blur-sm">
                  <VideoControls settings={settings} onChange={setSettings} />
                </div>
              </TabsContent>

              <TabsContent value="templates" className="mt-6">
                <div className="rounded-2xl border border-border bg-card p-6 backdrop-blur-sm">
                  <TemplateSelector
                    selected={selectedTemplate}
                    onSelect={setSelectedTemplate}
                  />
                </div>
              </TabsContent>
            </Tabs>

            {/* Generate Button */}
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Button
                onClick={handleGenerate}
                disabled={!prompt.trim() || isGenerating}
                className="w-full h-16 text-lg font-semibold bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 shadow-lg shadow-violet-500/50 transition-all hover:shadow-xl hover:shadow-violet-500/60"
              >
                {isGenerating ? (
                  <>
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                      className="mr-2"
                    >
                      <Sparkles className="w-5 h-5" />
                    </motion.div>
                    Generating Magic...
                  </>
                ) : (
                  <>
                    <Wand2 className="w-5 h-5 mr-2" />
                    Generate Video
                  </>
                )}
              </Button>
            </motion.div>
          </motion.div>

          {/* Right Panel - Preview & Progress */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-6"
          >
            {/* Preview */}
            <div className="rounded-2xl border border-border bg-card p-6 backdrop-blur-sm sticky top-8">
              <h2 className="text-xl font-semibold mb-4">Preview</h2>
              <VideoPreview url={videoUrl} isGenerating={isGenerating} />
              
              {/* Progress Tracker */}
              <AnimatePresence>
                {isGenerating && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-6"
                  >
                    <ProgressTracker
                      progress={progress}
                      stage={currentStage}
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Video Actions */}
              {videoUrl && !isGenerating && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-6 flex gap-2"
                >
                  <Button variant="outline" className="flex-1">
                    <Play className="w-4 h-4 mr-2" />
                    Play
                  </Button>
                  <Button variant="outline" className="flex-1">
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                </motion.div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
