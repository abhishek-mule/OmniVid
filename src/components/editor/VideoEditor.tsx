'use client';

import { useState } from 'react';
import {
  Video,
  Upload,
  Scissors,
  Wand2,
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Download,
  Layers,
  Type,
  Music,
  Image as ImageIcon,
  Sparkles,
  Settings,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function VideoEditor() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration] = useState(120);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-4">
      <div className="max-w-[1800px] mx-auto">
        <header className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Video className="w-8 h-8 text-cyan-400" strokeWidth={1.5} />
            <div>
              <h1 className="text-2xl font-bold text-white">OmniVid Editor</h1>
              <p className="text-sm text-slate-400">AI-Powered Video Creation</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button variant="outline" className="gap-2">
              <Settings className="w-4 h-4" />
              <span>Settings</span>
            </Button>
            <Button className="gap-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:shadow-lg hover:shadow-cyan-500/50">
              <Sparkles className="w-4 h-4" />
              <span>Generate Video</span>
            </Button>
          </div>
        </header>

        <div className="grid grid-cols-12 gap-4 h-[calc(100vh-180px)]">
          {/* Left Panel - Media Library */}
          <div className="col-span-2 bg-slate-900/50 rounded-xl p-4 border border-slate-800/50">
            <h2 className="text-sm font-medium text-slate-300 mb-4">MEDIA LIBRARY</h2>
            <div className="space-y-3">
              <Button variant="outline" className="w-full justify-start gap-2">
                <Upload className="w-4 h-4" />
                <span>Upload Media</span>
              </Button>
              <Button variant="outline" className="w-full justify-start gap-2">
                <ImageIcon className="w-4 h-4" />
                <span>Images</span>
              </Button>
              <Button variant="outline" className="w-full justify-start gap-2">
                <Video className="w-4 h-4" />
                <span>Videos</span>
              </Button>
              <Button variant="outline" className="w-full justify-start gap-2">
                <Music className="w-4 h-4" />
                <span>Audio</span>
              </Button>
            </div>
          </div>

          {/* Main Preview */}
          <div className="col-span-7 bg-black rounded-xl overflow-hidden border border-slate-800/50 flex flex-col">
            <div className="flex-1 bg-gradient-to-br from-slate-900 to-slate-950 flex items-center justify-center">
              <div className="text-center p-8">
                <Video className="w-16 h-16 mx-auto text-slate-700 mb-4" />
                <h3 className="text-xl font-medium text-slate-300 mb-2">Video Preview</h3>
                <p className="text-slate-500 text-sm">Your video will appear here</p>
              </div>
            </div>
            
            {/* Timeline Controls */}
            <div className="p-4 border-t border-slate-800/50 bg-slate-900/30">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-slate-400">{formatTime(currentTime)}</span>
                <div className="flex-1 mx-4">
                  <Slider
                    value={[currentTime]}
                    max={duration}
                    step={1}
                    onValueChange={([value]) => setCurrentTime(value)}
                    className="h-2"
                  />
                </div>
                <span className="text-xs text-slate-400">{formatTime(duration)}</span>
              </div>
              
              <div className="flex items-center justify-center gap-4">
                <Button variant="ghost" size="icon">
                  <SkipBack className="w-5 h-5" />
                </Button>
                <Button 
                  variant="default" 
                  size="lg" 
                  className="rounded-full w-14 h-14"
                  onClick={() => setIsPlaying(!isPlaying)}
                >
                  {isPlaying ? 
                    <Pause className="w-6 h-6" /> : 
                    <Play className="w-6 h-6 ml-1" />
                  }
                </Button>
                <Button variant="ghost" size="icon">
                  <SkipForward className="w-5 h-5" />
                </Button>
              </div>
            </div>
          </div>

          {/* Right Panel - Tools */}
          <div className="col-span-3 bg-slate-900/50 rounded-xl p-4 border border-slate-800/50 overflow-y-auto">
            <Tabs defaultValue="elements" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="elements">Elements</TabsTrigger>
                <TabsTrigger value="filters">Filters</TabsTrigger>
                <TabsTrigger value="export">Export</TabsTrigger>
              </TabsList>
              
              <TabsContent value="elements" className="mt-4 space-y-4">
                <div className="space-y-2">
                  <h3 className="text-sm font-medium text-slate-300">Add Elements</h3>
                  <div className="grid grid-cols-2 gap-2">
                    <Button variant="outline" className="flex-col h-auto py-3">
                      <Type className="w-5 h-5 mb-1" />
                      <span className="text-xs">Text</span>
                    </Button>
                    <Button variant="outline" className="flex-col h-auto py-3">
                      <ImageIcon className="w-5 h-5 mb-1" />
                      <span className="text-xs">Image</span>
                    </Button>
                    <Button variant="outline" className="flex-col h-auto py-3">
                      <Layers className="w-5 h-5 mb-1" />
                      <span className="text-xs">Shape</span>
                    </Button>
                    <Button variant="outline" className="flex-col h-auto py-3">
                      <Music className="w-5 h-5 mb-1" />
                      <span className="text-xs">Audio</span>
                    </Button>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <h3 className="text-sm font-medium text-slate-300">AI Tools</h3>
                  <div className="space-y-2">
                    <Button variant="outline" className="w-full justify-start gap-2">
                      <Wand2 className="w-4 h-4" />
                      <span>AI Enhance</span>
                    </Button>
                    <Button variant="outline" className="w-full justify-start gap-2">
                      <Scissors className="w-4 h-4" />
                      <span>Auto Cut</span>
                    </Button>
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="filters" className="mt-4">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <h3 className="text-sm font-medium text-slate-300">Filters</h3>
                    <div className="grid grid-cols-3 gap-2">
                      {['Vibrant', 'Moody', 'B&W', 'Retro', 'Cinematic', 'None'].map(filter => (
                        <Button 
                          key={filter}
                          variant="outline" 
                          size="sm"
                          className="text-xs h-16"
                        >
                          {filter}
                        </Button>
                      ))}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <h3 className="text-sm font-medium text-slate-300">Adjustments</h3>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs text-slate-400">
                        <span>Brightness</span>
                        <span>0</span>
                      </div>
                      <Slider defaultValue={[0]} max={100} step={1} />
                      
                      <div className="flex items-center justify-between text-xs text-slate-400">
                        <span>Contrast</span>
                        <span>0</span>
                      </div>
                      <Slider defaultValue={[0]} max={100} step={1} />
                      
                      <div className="flex items-center justify-between text-xs text-slate-400">
                        <span>Saturation</span>
                        <span>0</span>
                      </div>
                      <Slider defaultValue={[0]} max={100} step={1} />
                    </div>
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="export" className="mt-4 space-y-4">
                <div className="space-y-2">
                  <h3 className="text-sm font-medium text-slate-300">Export Settings</h3>
                  <div className="space-y-2">
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">Resolution</label>
                      <select className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-sm text-white">
                        <option>1920x1080 (Full HD)</option>
                        <option>1280x720 (HD)</option>
                        <option>854x480 (480p)</option>
                        <option>640x360 (360p)</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">Format</label>
                      <select className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-sm text-white">
                        <option>MP4</option>
                        <option>MOV</option>
                        <option>GIF</option>
                      </select>
                    </div>
                    
                    <div className="pt-2">
                      <Button className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:shadow-lg hover:shadow-cyan-500/50">
                        <Download className="w-4 h-4 mr-2" />
                        Export Video
                      </Button>
                    </div>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  );
}
