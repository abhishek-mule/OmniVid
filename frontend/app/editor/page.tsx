'use client';

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import { Tabs, TabsContent } from "@/components/ui/tabs";
import { useState } from "react";
import { Play, Square, Upload, Scissors, Type, Music, Settings, Save, Download } from "lucide-react";

export default function VideoEditorPage() {
  const [activeTab, setActiveTab] = useState('media');
  const [isPlaying, setIsPlaying] = useState(false);

  const navItems = [
    { id: 'media', icon: <Upload className="h-5 w-5" />, label: 'Media' },
    { id: 'cut', icon: <Scissors className="h-5 w-5" />, label: 'Cut' },
    { id: 'text', icon: <Type className="h-5 w-5" />, label: 'Text' },
    { id: 'audio', icon: <Music className="h-5 w-5" />, label: 'Audio' },
    { id: 'settings', icon: <Settings className="h-5 w-5" />, label: 'Settings' },
  ];

  return (
    <div className="flex h-screen flex-col gradient-bg">
      {/* Top Bar */}
      <header className="glass border-b border-white/10 px-6 py-4 flex items-center justify-between premium-shadow">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
            <span className="text-white font-bold text-sm">O</span>
          </div>
          <div>
            <h1 className="font-bold text-gradient">OmniVid Editor</h1>
            <span className="text-muted-foreground text-sm">My Project</span>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline" size="sm" className="glass-hover gap-2">
            <Save className="h-4 w-4" />
            Save
          </Button>
          <Button size="sm" className="gradient-primary text-white gap-2">
            <Download className="h-4 w-4" />
            Export
          </Button>
        </div>
      </header>
      
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <ResizablePanelGroup direction="horizontal" className="h-full">
          <ResizablePanel defaultSize={15} minSize={10} maxSize={20} className="border-r">
            <div className="p-2 space-y-1">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === item.id
                      ? 'bg-muted text-foreground'
                      : 'text-muted-foreground hover:bg-muted/50'
                  }`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
          </ResizablePanel>
          
          <ResizableHandle withHandle className="w-1 bg-border hover:bg-primary/50 transition-colors" />
          
          {/* Main Content */}
          <ResizablePanel defaultSize={60}>
            <div className="flex flex-col h-full">
              {/* Preview Area */}
              <div className="flex-1 flex items-center justify-center bg-muted/50 p-4">
                <div className="w-full max-w-2xl aspect-video bg-black rounded-lg overflow-hidden">
                  <div className="h-full flex items-center justify-center text-muted-foreground">
                    {isPlaying ? (
                      <div className="w-full h-full bg-gray-900 flex items-center justify-center">
                        <span>Video Preview</span>
                      </div>
                    ) : (
                      <div className="text-center">
                        <div className="mx-auto w-16 h-16 bg-muted/50 rounded-full flex items-center justify-center mb-4">
                          <Play className="h-8 w-8 ml-1" />
                        </div>
                        <p>Click play to preview your video</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Timeline */}
              <div className="border-t h-32 p-2">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex space-x-2">
                    <Button variant="ghost" size="sm" onClick={() => setIsPlaying(!isPlaying)}>
                      {isPlaying ? (
                        <Square className="h-4 w-4 mr-1" />
                      ) : (
                        <Play className="h-4 w-4 mr-1" />
                      )}
                      {isPlaying ? 'Stop' : 'Play'}
                    </Button>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    00:00:00 / 00:01:30
                  </div>
                </div>
                
                <div className="bg-muted/50 rounded h-16 overflow-hidden">
                  <div className="h-full flex items-center px-4">
                    <div className="h-12 w-20 bg-primary/20 rounded flex-shrink-0"></div>
                    <div className="h-12 w-32 bg-secondary/20 rounded ml-2 flex-shrink-0"></div>
                    <div className="h-12 w-24 bg-destructive/20 rounded ml-2 flex-shrink-0"></div>
                    <div className="h-12 w-16 bg-green-500/20 rounded ml-2 flex-shrink-0"></div>
                  </div>
                </div>
              </div>
            </div>
          </ResizablePanel>
          
          <ResizableHandle withHandle className="w-1 bg-border hover:bg-primary/50 transition-colors" />
          
          {/* Right Sidebar */}
          <ResizablePanel defaultSize={25} minSize={15} maxSize={30} className="border-l">
            <Tabs defaultValue="properties" className="h-full flex flex-col">
              <div className="p-4 border-b">
                <h2 className="font-semibold">
                  {activeTab === 'media' && 'Media Library'}
                  {activeTab === 'cut' && 'Trim & Cut'}
                  {activeTab === 'text' && 'Add Text'}
                  {activeTab === 'audio' && 'Audio Tracks'}
                  {activeTab === 'settings' && 'Project Settings'}
                </h2>
              </div>
              
              <TabsContent value="properties" className="flex-1 overflow-auto p-4">
                {activeTab === 'media' && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-2">
                      {[1, 2, 3, 4, 5, 6].map((i) => (
                        <div key={i} className="aspect-video bg-muted rounded cursor-pointer hover:ring-2 hover:ring-primary">
                          <div className="h-full flex items-center justify-center text-muted-foreground">
                            Media {i}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {activeTab === 'text' && (
                  <div className="space-y-4">
                    <Button variant="outline" className="w-full">
                      Add Text Layer
                    </Button>
                    <div className="space-y-2">
                      <h3 className="font-medium">Text Properties</h3>
                      <div className="space-y-2">
                        <Input placeholder="Enter your text here" />
                        <div className="grid grid-cols-2 gap-2">
                          <select className="border rounded p-2 text-sm">
                            <option>Arial</option>
                            <option>Roboto</option>
                            <option>Open Sans</option>
                            <option>Montserrat</option>
                          </select>
                          <select className="border rounded p-2 text-sm">
                            <option>16px</option>
                            <option>24px</option>
                            <option>32px</option>
                            <option>48px</option>
                          </select>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm">B</Button>
                          <Button variant="outline" size="sm">I</Button>
                          <Button variant="outline" size="sm">U</Button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {activeTab === 'settings' && (
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <h3 className="font-medium">Project Settings</h3>
                      <div className="space-y-2">
                        <div>
                          <Label>Project Name</Label>
                          <Input value="My Project" />
                        </div>
                        <div>
                          <Label>Resolution</Label>
                          <select className="w-full border rounded p-2 text-sm">
                            <option>1920x1080 (16:9)</option>
                            <option>1080x1920 (9:16)</option>
                            <option>1080x1080 (1:1)</option>
                            <option>Custom...</option>
                          </select>
                        </div>
                        <div>
                          <Label>Frame Rate</Label>
                          <select className="w-full border rounded p-2 text-sm">
                            <option>24 FPS (Film)</option>
                            <option>30 FPS (Standard)</option>
                            <option>60 FPS (Smooth)</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  );
}
