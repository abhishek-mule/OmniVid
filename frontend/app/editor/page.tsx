'use client';

import { useState, useRef, useEffect } from 'react';
import { 
  Play, 
  Download, 
  Settings, 
  Sparkles, 
  Clock, 
  ChevronDown,
  Check,
  Loader2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Slider } from '@/components/ui/slider';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from '@/components/ui/tabs';
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardDescription,
  CardFooter
} from '@/components/ui/card';
import { 
  Progress 
} from '@/components/ui/progress';
// Removed Select components (using native <select> elements instead)
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { simpleApi, TemplateItem } from '@omnivid/shared/lib';

// Types
// Removed unused Template type

type RecentVideo = {
  id: string;
  name: string;
  date: string;
};

// Mock data for templates
// Removed unused TEMPLATES mock

// Mock recent videos
const RECENT_VIDEOS: RecentVideo[] = [
  { id: '1', name: 'Summer Sale Promo', date: '2 hours ago' },
  { id: '2', name: 'Product Demo', date: '1 day ago' },
  { id: '3', name: 'Company Intro', date: '3 days ago' },
];

// Animation variants
const fadeIn = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

export default function EditorPage() {
  // State
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState<'idle' | 'parsing' | 'generating' | 'rendering' | 'complete'>('idle');
  const [settings, setSettings] = useState({
    resolution: '1080p',
    fps: 30,
    quality: 'high',
    showAdvanced: false,
    aspectRatio: '16:9',
  });
  const [, setVideoId] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [templateFilter, setTemplateFilter] = useState<string>('all');
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Helper: stage progress threshold for UI indicators
  const getStageProgress = (stage: 'parsing' | 'generating' | 'rendering') => {
    switch (stage) {
      case 'parsing':
        return 33;
      case 'generating':
        return 66;
      case 'rendering':
        return 99;
      default:
        return 0;
    }
  };

  // Helper: map backend stage text to our normalized stages
  const normalizeStage = (text: string): 'parsing' | 'generating' | 'rendering' | 'complete' => {
    const s = (text || '').toLowerCase();
    if (s.includes('analyzing')) return 'parsing';
    if (s.includes('generating') || s.includes('creating')) return 'generating';
    if (s.includes('rendering') || s.includes('finalizing')) return 'rendering';
    if (s.includes('complete')) return 'complete';
    return 'generating';
  };

  // Derived: templates filtered by category
  const filteredTemplates = templates.filter((t) => templateFilter === 'all' ? true : t.category === templateFilter);

  // Fetch templates on mount
  useEffect(() => {
    simpleApi.listTemplates()
      .then(setTemplates)
      .catch(() => setTemplates([]));
  }, []);

  // Clean up WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    // Reset state
    setIsGenerating(true);
    setCurrentStage('parsing');
    setProgress(0);
    setVideoUrl(null);

    try {
      const payload = {
        prompt,
        settings: {
          resolution: settings.resolution,
          fps: settings.fps,
          duration: 15,
          quality: settings.quality,
          template: selectedTemplateId ?? undefined,
        },
      };

      const resp = await simpleApi.createVideo(payload);
      const vid = resp.video_id;
      setVideoId(vid);

      // Open WebSocket for real-time progress
      const wsUrl = simpleApi.getWebSocketUrl(vid);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        // Optional: send a hello/ping
        try { ws.send(JSON.stringify({ type: 'ping', ts: Date.now() })); } catch {}
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'connection' || msg.type === 'ping' || msg.type === 'pong') return;

          const p = typeof msg.progress === 'number' ? msg.progress : progress;
          setProgress(Math.max(0, Math.min(100, p)));

          if (typeof msg.stage === 'string') {
            setCurrentStage(normalizeStage(msg.stage));
          }

          if (p >= 100 || msg.status === 'completed') {
            setIsGenerating(false);
            setCurrentStage('complete');
            if (msg.output_url) {
              const base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
              setVideoUrl(`${base}${msg.output_url}`);
            }
            try { ws.close(); } catch {}
          }
        } catch (e) {
          console.error('WS message error', e);
        }
      };

      ws.onerror = (e) => {
        console.error('WS error', e);
      };

      ws.onclose = () => {
        // no-op
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('Failed to start generation', err);
      setIsGenerating(false);
      setCurrentStage('idle');
    }
  };

  const handleDownload = () => {
    if (videoUrl) {
      window.open(videoUrl, '_blank');
    }
  };

  const handleTemplateSelect = (template: TemplateItem) => {
    setSelectedTemplateId(template.id);
    setPrompt(`Create a ${template.name.toLowerCase()} video`);
  };

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Left Panel - Input Controls */}
      <div className="w-80 border-r border-gray-200 bg-white p-4 flex flex-col">
        <h2 className="text-lg font-semibold mb-4">Video Generator</h2>
        
        <div className="space-y-4 flex-1 overflow-y-auto">
          {/* Prompt Input */}
          <motion.div 
            initial="hidden"
            animate="visible"
            variants={fadeIn}
            className="space-y-1"
          >
            <label className="block text-sm font-medium text-gray-700">Describe your video</label>
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="A futuristic tech intro with glowing particles..."
              className="min-h-[120px] text-sm"
              disabled={isGenerating}
            />
            <p className="text-xs text-gray-500 mt-1">Be as descriptive as possible for better results</p>
          </motion.div>

          {/* Resolution Selector */}
          <motion.div 
            initial="hidden"
            animate="visible"
            variants={fadeIn}
            transition={{ delay: 0.1 }}
          >
            <label className="block text-sm font-medium text-gray-700 mb-1">Resolution</label>
            <select
              className="w-full h-10 px-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              value={settings.resolution}
              onChange={(e) => setSettings({ ...settings, resolution: e.target.value })}
              disabled={isGenerating}
            >
              <option value="720p">720p (HD)</option>
              <option value="1080p">1080p (Full HD)</option>
              <option value="4k">4K (UHD)</option>
            </select>
          </motion.div>

          {/* FPS Slider */}
          <motion.div 
            initial="hidden"
            animate="visible"
            variants={fadeIn}
            transition={{ delay: 0.15 }}
            className="space-y-2"
          >
            <div className="flex justify-between items-center">
              <label className="text-sm font-medium text-gray-700">Frames per second</label>
              <span className="text-sm font-mono bg-gray-100 px-2 py-0.5 rounded">{settings.fps} FPS</span>
            </div>
            <Slider
              value={[settings.fps]}
              onValueChange={([value]) => setSettings({...settings, fps: value})}
              min={24}
              max={60}
              step={1}
              disabled={isGenerating}
              className="py-4"
            />
          </motion.div>

          {/* Generate Button */}
          <motion.div 
            initial="hidden"
            animate="visible"
            variants={fadeIn}
            transition={{ delay: 0.2 }}
            className="pt-2"
          >
            <Button 
              onClick={handleGenerate} 
              className="w-full h-11 text-base font-medium"
              disabled={isGenerating || !prompt.trim()}
              size="lg"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Generate Video
                </>
              )}
            </Button>
          </motion.div>

          {/* Advanced Options */}
          <motion.div 
            initial="hidden"
            animate="visible"
            variants={fadeIn}
            transition={{ delay: 0.25 }}
            className="pt-2 border-t border-gray-200"
          >
            <button 
              className="flex items-center justify-between w-full text-sm font-medium text-gray-700 hover:text-gray-900 py-2"
              onClick={() => setSettings({...settings, showAdvanced: !settings.showAdvanced})}
            >
              <span className="flex items-center">
                <Settings className="w-4 h-4 mr-2" />
                Advanced Options
              </span>
              <ChevronDown className={cn(
                "w-4 h-4 transition-transform",
                settings.showAdvanced ? "rotate-180" : ""
              )} />
            </button>
            
            <AnimatePresence>
              {settings.showAdvanced && (
                <motion.div 
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden"
                >
                  <div className="mt-3 space-y-4 p-3 bg-gray-50 rounded-md">
                    {/* Quality Selector */}
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Quality</label>
                      <select
                        className="w-full h-8 px-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                        value={settings.quality}
                        onChange={(e) => setSettings({ ...settings, quality: e.target.value })}
                      >
                        <option value="low">Low (Faster)</option>
                        <option value="medium">Medium</option>
                        <option value="high">High (Better Quality)</option>
                      </select>
                    </div>

                    {/* Additional advanced options can be added here */}
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Aspect Ratio</label>
                      <div className="grid grid-cols-3 gap-2">
                        {['16:9', '1:1', '9:16'].map((ratio) => (
                          <button
                            key={ratio}
                            className={cn(
                              "text-xs py-1.5 px-2 rounded border",
                              settings.aspectRatio === ratio 
                                ? "bg-blue-50 border-blue-500 text-blue-700" 
                                : "border-gray-300 text-gray-700 hover:bg-gray-50"
                            )}
                            onClick={() => setSettings({...settings, aspectRatio: ratio})}
                          >
                            {ratio}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>

      {/* Center Canvas - Preview */}
      <div className="flex-1 flex flex-col p-4 overflow-hidden">
        <div className={cn(
          "rounded-xl border-2 border-dashed flex items-center justify-center",
          isGenerating ? "bg-gray-50 border-gray-200" : "border-gray-300 bg-white/50",
          "flex-1 overflow-hidden relative transition-colors duration-200"
        )}>
          {currentStage === 'complete' ? (
            <div className="w-full h-full relative group">
              <video
                ref={videoRef}
                src={videoUrl ?? "/sample-output.mp4"}
                className="w-full h-full object-contain"
                controls
                autoPlay
                loop
              />
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute bottom-4 right-4 flex space-x-2"
              >
                <Button 
                  variant="outline"
                  size="sm"
                  className="bg-white/90 hover:bg-white backdrop-blur-sm shadow-sm"
                  onClick={() => {
                    if (videoRef.current) {
                      videoRef.current.paused ? videoRef.current.play() : videoRef.current.pause();
                    }
                  }}
                >
                  <Play className="w-4 h-4 mr-1.5" />
                  Play/Pause
                </Button>
                <Button 
                  onClick={handleDownload}
                  className="bg-blue-600 hover:bg-blue-700 text-white shadow-sm"
                  size="sm"
                >
                  <Download className="w-4 h-4 mr-1.5" />
                  Download
                </Button>
              </motion.div>
            </div>
          ) : (
            <motion.div 
              className="text-center p-8 max-w-md"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-blue-50 flex items-center justify-center">
                {isGenerating ? (
                  <motion.div 
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  >
                    <Loader2 className="w-8 h-8 text-blue-500" />
                  </motion.div>
                ) : (
                  <Sparkles className="w-8 h-8 text-blue-500" />
                )}
              </div>
              
              <h3 className="font-medium text-lg mb-1 text-gray-900">
                {isGenerating ? (
                  <span>Creating your video...</span>
                ) : (
                  <span>Your video will appear here</span>
                )}
              </h3>
              
              <p className="text-sm text-gray-500 mb-6">
                {isGenerating 
                  ? 'This may take a few moments. Please wait...'
                  : 'Enter a prompt and click Generate to create your video.'}
              </p>
              
              {isGenerating && (
                <motion.div 
                  className="space-y-4 mt-6 max-w-md mx-auto"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  {/* Progress Bar */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                      <span className="font-medium">
                        {currentStage === 'parsing' && 'Analyzing prompt...'}
                        {currentStage === 'generating' && 'Generating animation...'}
                        {currentStage === 'rendering' && 'Finalizing video...'}
                      </span>
                      <span className="font-mono">{Math.round(progress)}%</span>
                    </div>
                    <Progress value={progress} className="h-2" />
                  </div>
                  
                  {/* Stage Indicators */}
                  <div className="flex justify-between text-xs text-gray-500 pt-2">
                    {(['parsing', 'generating', 'rendering'] as const).map((stage) => (
                      <div key={stage} className="flex flex-col items-center space-y-1">
                        <div className={cn(
                          "w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium",
                          currentStage === stage 
                            ? "bg-blue-100 text-blue-600" 
                            : progress >= getStageProgress(stage)
                              ? "bg-green-100 text-green-600"
                              : "bg-gray-100 text-gray-400"
                        )}>
                          {progress >= getStageProgress(stage) ? (
                            <Check className="w-3 h-3" />
                          ) : currentStage === stage ? (
                            <Loader2 className="w-3 h-3 animate-spin" />
                          ) : (
                            <span>•</span>
                          )}
                        </div>
                        <span className="text-[10px] capitalize">{stage}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}
        </div>
        
        {/* Timeline */}
        {isGenerating && (
          <motion.div 
            className="mt-4 bg-white p-3 rounded-lg border border-gray-200 shadow-sm"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="flex justify-between text-xs text-gray-600 mb-2">
              <span>Generation Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <motion.div 
                className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </motion.div>
        )}
      </div>

      {/* Right Sidebar - Templates/History */}
      <div className="w-80 border-l border-gray-200 bg-white flex flex-col">
        <Tabs defaultValue="templates" className="flex-1 flex flex-col">
          <TabsList className="grid w-full grid-cols-2 rounded-none border-b">
            <TabsTrigger value="templates" className="py-4">Templates</TabsTrigger>
            <TabsTrigger value="history" className="py-4">History</TabsTrigger>
          </TabsList>
          
          <TabsContent 
            value="templates" 
            className="flex-1 overflow-y-auto p-4 m-0"
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-medium text-gray-900">Templates</h3>
              <div className="relative">
                <select 
                  className="appearance-none bg-white border border-gray-200 rounded-md text-xs py-1.5 pl-2 pr-6 text-gray-700 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  value={templateFilter}
                  onChange={(e) => setTemplateFilter(e.target.value)}
                >
                  <option value="all">All Categories</option>
                  <option value="Business">Business</option>
                  <option value="Social">Social</option>
                  <option value="E-commerce">E-commerce</option>
                </select>
                <ChevronDown className="w-3.5 h-3.5 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
              </div>
            </div>
            
            <div className="space-y-3">
              {filteredTemplates.map((template) => (
                <motion.div
                  key={template.id}
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                >
                  <Card 
                    className={cn(
                      "cursor-pointer transition-all overflow-hidden group",
                      selectedTemplateId === template.id 
                        ? "ring-2 ring-blue-500 border-blue-500" 
                        : "hover:border-blue-300"
                    )}
                    onClick={() => handleTemplateSelect(template)}
                  >
                    <CardHeader className="p-3 pb-2 space-y-2">
                      <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 rounded overflow-hidden relative">
                        <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                          <Play className="w-8 h-8 opacity-70 group-hover:opacity-100 transition-opacity" />
                        </div>
                        <div className="absolute bottom-2 right-2 bg-black/60 text-white text-[10px] px-1.5 py-0.5 rounded">
                          {template.category}
                        </div>
                      </div>
                      <CardTitle className="text-sm font-medium line-clamp-1">
                        {template.name}
                      </CardTitle>
                      <CardDescription className="text-xs line-clamp-2">
                        {template.description}
                      </CardDescription>
                    </CardHeader>
                    <CardFooter className="p-3 pt-0">
                      <Button 
                        variant={selectedTemplateId === template.id ? "default" : "outline"}
                        size="sm" 
                        className="w-full text-xs h-8"
                      >
                        {selectedTemplateId === template.id ? "Selected" : "Use Template"}
                      </Button>
                    </CardFooter>
                  </Card>
                </motion.div>
              ))}
            </div>
          </TabsContent>
          
          <TabsContent 
            value="history" 
            className="flex-1 overflow-y-auto p-4 m-0"
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-medium text-gray-900">Recent Videos</h3>
              <Button variant="ghost" size="sm" className="text-xs text-blue-600 hover:text-blue-700">
                View All
              </Button>
            </div>
            
            <div className="space-y-2">
              {RECENT_VIDEOS.map((video, index) => (
                <motion.div
                  key={video.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <div 
                    className={cn(
                      "p-3 border rounded-md hover:bg-gray-50 cursor-pointer transition-colors flex items-center",
                      index === 0 && "border-blue-200 bg-blue-50"
                    )}
                  >
                    <div className="w-10 h-10 rounded bg-gray-100 flex-shrink-0 flex items-center justify-center mr-3">
                      <Clock className="w-4 h-4 text-gray-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate">{video.name}</div>
                      <div className="flex items-center text-xs text-gray-500">
                        <span>{video.date}</span>
                        {index === 0 && (
                          <span className="ml-2 px-1.5 py-0.5 bg-blue-100 text-blue-700 text-[10px] font-medium rounded">
                            Latest
                          </span>
                        )}
                      </div>
                    </div>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="h-7 w-7 text-gray-400 hover:text-gray-700"
                      onClick={(e) => {
                        e.stopPropagation();
                        // Handle download
                      }}
                    >
                      <Download className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </motion.div>
              ))}
            </div>
            
            {RECENT_VIDEOS.length === 0 && (
              <div className="text-center py-8 text-sm text-gray-500">
                <p>No recent videos yet</p>
                <p className="text-xs mt-1">Your generated videos will appear here</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
