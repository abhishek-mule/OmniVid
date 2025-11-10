'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Sparkles, Image, Video, Music, Type, ChevronDown, Loader2, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

type GenerationType = 'video' | 'image' | 'audio' | 'text';

const styles = [
  'Cinematic', 'Anime', '3D Render', 'Watercolor', 'Pixel Art',
  'Cyberpunk', 'Minimalist', 'Retro', 'Futuristic', 'Hand-drawn'
];

export default function GeneratePage() {
  const router = useRouter();
  const [prompt, setPrompt] = useState('');
  const [selectedType, setSelectedType] = useState<GenerationType>('video');
  const [selectedStyle, setSelectedStyle] = useState<string>(styles[0]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStyleDropdownOpen, setIsStyleDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // In a real app, you would navigate to the editor with the generated content
      router.push('/editor');
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setIsLoading(false);
    }
  };



  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 mb-4">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-3">Generate with AI</h1>
          <p className="text-lg text-slate-400">
            Create amazing content with the power of artificial intelligence
          </p>
        </header>

        <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-white">What would you like to create?</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs 
              defaultValue="video" 
              className="w-full"
              onValueChange={(value) => setSelectedType(value as GenerationType)}
            >
              <TabsList className="grid w-full grid-cols-4 bg-slate-800/50 border border-slate-700/50 mb-6">
                <TabsTrigger value="video" className="flex items-center">
                  <Video className="w-4 h-4 mr-2" />
                  <span>Video</span>
                </TabsTrigger>
                <TabsTrigger value="image" className="flex items-center">
                  <Image className="w-4 h-4 mr-2" />
                  <span>Image</span>
                </TabsTrigger>
                <TabsTrigger value="audio" className="flex items-center">
                  <Music className="w-4 h-4 mr-2" />
                  <span>Audio</span>
                </TabsTrigger>
                <TabsTrigger value="text" className="flex items-center">
                  <Type className="w-4 h-4 mr-2" />
                  <span>Text</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value={selectedType} className="space-y-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">
                    Describe what you want to create
                  </label>
                  <Textarea
                    placeholder={`Describe the ${selectedType} you want to generate...`}
                    className="min-h-[120px] bg-slate-800/50 border-slate-700/50 text-white placeholder-slate-500"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                  />
                </div>

                <div className="flex flex-col sm:flex-row gap-4">
                  <div className="w-full sm:w-1/2">
                    <label className="text-sm font-medium text-slate-300 mb-2 block">
                      Style
                    </label>
                    <div className="relative" ref={dropdownRef}>
                      <button
                        type="button"
                        className="w-full flex items-center justify-between px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-lg text-slate-300 hover:border-slate-600 transition-colors"
                        onClick={() => setIsStyleDropdownOpen(!isStyleDropdownOpen)}
                      >
                        <span>{selectedStyle}</span>
                        <ChevronDown className={`w-4 h-4 transition-transform ${isStyleDropdownOpen ? 'rotate-180' : ''}`} />
                      </button>
                      
                      {isStyleDropdownOpen && (
                        <div className="absolute z-10 mt-1 w-full bg-slate-800 border border-slate-700/50 rounded-lg shadow-lg">
                          <div className="max-h-60 overflow-y-auto">
                            {styles.map((style) => (
                              <button
                                key={style}
                                className={`w-full text-left px-4 py-2 text-sm ${
                                  selectedStyle === style 
                                    ? 'bg-slate-700/50 text-white' 
                                    : 'text-slate-300 hover:bg-slate-700/30'
                                }`}
                                onClick={() => {
                                  setSelectedStyle(style);
                                  setIsStyleDropdownOpen(false);
                                }}
                              >
                                {style}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="w-full sm:w-1/2">
                    <label className="text-sm font-medium text-slate-300 mb-2 block">
                      Duration
                    </label>
                    <select 
                      className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-lg text-slate-300 hover:border-slate-600 transition-colors appearance-none"
                    >
                      <option>15 seconds</option>
                      <option>30 seconds</option>
                      <option>1 minute</option>
                      <option>2 minutes</option>
                      <option>5 minutes</option>
                    </select>
                  </div>
                </div>

                <div className="pt-2">
                  <Button
                    className="w-full h-12 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-medium rounded-lg transition-all duration-300 flex items-center justify-center"
                    onClick={handleGenerate}
                    disabled={isLoading || !prompt.trim()}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-5 h-5 mr-2" />
                        Generate {selectedType.charAt(0).toUpperCase() + selectedType.slice(1)}
                      </>
                    )}
                  </Button>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 bg-slate-800/50 border border-slate-700/50 rounded-xl">
            <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center mb-4">
              <Sparkles className="w-5 h-5 text-cyan-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">AI-Powered</h3>
            <p className="text-slate-400 text-sm">
              Leverage the latest in AI technology to create stunning content in seconds.
            </p>
          </div>

          <div className="p-6 bg-slate-800/50 border border-slate-700/50 rounded-xl">
            <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center mb-4">
              <Video className="w-5 h-5 text-purple-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Multiple Formats</h3>
            <p className="text-slate-400 text-sm">
              Generate videos, images, audio, and text all from one platform.
            </p>
          </div>

          <div className="p-6 bg-slate-800/50 border border-slate-700/50 rounded-xl">
            <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center mb-4">
              <Zap className="w-5 h-5 text-green-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Lightning Fast</h3>
            <p className="text-slate-400 text-sm">
              Get your content generated in seconds, not hours.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
