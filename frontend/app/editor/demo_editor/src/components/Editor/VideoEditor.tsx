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
  Volume2,
  Maximize,
  Download,
  Layers,
  Type,
  Music,
  Image as ImageIcon,
  Sparkles,
  Settings,
} from 'lucide-react';

export default function VideoEditor() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(120);

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
            <button className="px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white hover:border-cyan-500/50 transition-all flex items-center gap-2">
              <Settings className="w-4 h-4" />
              <span className="text-sm">Settings</span>
            </button>
            <button className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg font-medium transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/50 flex items-center gap-2">
              <Download className="w-4 h-4" />
              <span>Export Video</span>
            </button>
          </div>
        </header>

        <div className="grid grid-cols-12 gap-4 h-[calc(100vh-140px)]">
          <div className="col-span-2 bg-slate-900/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-4 overflow-y-auto">
            <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              Tools
            </h2>

            <div className="space-y-2">
              {[
                { icon: Upload, label: 'Import Media', color: 'cyan' },
                { icon: Scissors, label: 'Trim & Cut', color: 'blue' },
                { icon: Type, label: 'Add Text', color: 'violet' },
                { icon: Music, label: 'Add Audio', color: 'green' },
                { icon: ImageIcon, label: 'Add Image', color: 'orange' },
                { icon: Wand2, label: 'AI Effects', color: 'pink' },
                { icon: Sparkles, label: 'Transitions', color: 'yellow' },
              ].map((tool, idx) => (
                <button
                  key={idx}
                  className="w-full flex items-center gap-3 px-3 py-2.5 bg-slate-800/50 border border-slate-700/50 rounded-lg text-slate-300 hover:text-white hover:border-cyan-500/50 hover:bg-slate-800 transition-all text-sm"
                >
                  <tool.icon className="w-4 h-4" />
                  <span>{tool.label}</span>
                </button>
              ))}
            </div>

            <div className="mt-6">
              <h3 className="text-sm font-semibold text-white mb-3">AI Assistant</h3>
              <div className="p-3 bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-lg">
                <Sparkles className="w-5 h-5 text-cyan-400 mb-2" />
                <p className="text-xs text-slate-300 leading-relaxed">
                  Describe what you want to create and let AI generate it for you.
                </p>
                <button className="mt-3 w-full px-3 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg text-xs font-medium hover:shadow-lg transition-all">
                  Try AI Generation
                </button>
              </div>
            </div>
          </div>

          <div className="col-span-7 space-y-4">
            <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 h-[calc(100%-200px)]">
              <div className="w-full h-full bg-slate-950 rounded-xl flex items-center justify-center relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5"></div>
                <div className="relative text-center">
                  <div className="w-20 h-20 mx-auto mb-4 bg-slate-800 rounded-full flex items-center justify-center">
                    <Video className="w-10 h-10 text-slate-600" />
                  </div>
                  <p className="text-slate-500 text-lg mb-2">No video loaded</p>
                  <p className="text-slate-600 text-sm">Import media or generate with AI</p>
                </div>

                <button className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-slate-950/50 backdrop-blur-sm">
                  <div className="w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full flex items-center justify-center shadow-2xl shadow-cyan-500/50 transform hover:scale-110 transition-transform">
                    <Play className="w-8 h-8 text-white ml-1" fill="white" />
                  </div>
                </button>
              </div>
            </div>

            <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-4">
              <div className="flex items-center gap-4 mb-4">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="w-10 h-10 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full flex items-center justify-center hover:shadow-lg hover:shadow-cyan-500/50 transition-all"
                >
                  {isPlaying ? (
                    <Pause className="w-5 h-5 text-white" fill="white" />
                  ) : (
                    <Play className="w-5 h-5 text-white ml-0.5" fill="white" />
                  )}
                </button>

                <button className="w-8 h-8 bg-slate-800 rounded-lg flex items-center justify-center hover:bg-slate-700 transition-colors">
                  <SkipBack className="w-4 h-4 text-slate-400" />
                </button>

                <button className="w-8 h-8 bg-slate-800 rounded-lg flex items-center justify-center hover:bg-slate-700 transition-colors">
                  <SkipForward className="w-4 h-4 text-slate-400" />
                </button>

                <div className="flex-1 flex items-center gap-3">
                  <span className="text-sm text-slate-400 font-mono">{formatTime(currentTime)}</span>
                  <div className="flex-1 relative">
                    <input
                      type="range"
                      min="0"
                      max={duration}
                      value={currentTime}
                      onChange={(e) => setCurrentTime(Number(e.target.value))}
                      className="w-full h-1 bg-slate-700 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:bg-cyan-500 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:cursor-pointer"
                    />
                  </div>
                  <span className="text-sm text-slate-400 font-mono">{formatTime(duration)}</span>
                </div>

                <div className="flex items-center gap-2">
                  <Volume2 className="w-4 h-4 text-slate-400" />
                  <input
                    type="range"
                    min="0"
                    max="100"
                    defaultValue="70"
                    className="w-20 h-1 bg-slate-700 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-2.5 [&::-webkit-slider-thumb]:h-2.5 [&::-webkit-slider-thumb]:bg-cyan-500 [&::-webkit-slider-thumb]:rounded-full"
                  />
                </div>

                <button className="w-8 h-8 bg-slate-800 rounded-lg flex items-center justify-center hover:bg-slate-700 transition-colors">
                  <Maximize className="w-4 h-4 text-slate-400" />
                </button>
              </div>

              <div className="relative h-24 bg-slate-950 rounded-lg overflow-hidden">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full h-12 bg-gradient-to-r from-cyan-500/20 via-blue-500/20 to-cyan-500/20 opacity-50"></div>
                </div>
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                  <div className="w-0.5 h-16 bg-cyan-400 shadow-lg shadow-cyan-500/50"></div>
                </div>
              </div>
            </div>
          </div>

          <div className="col-span-3 bg-slate-900/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-4 overflow-y-auto">
            <h2 className="text-sm font-semibold text-white mb-4">Properties</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-2">Video Quality</label>
                <select className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:border-cyan-500">
                  <option>1080p HD</option>
                  <option>4K Ultra HD</option>
                  <option>720p</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-2">Frame Rate</label>
                <select className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:border-cyan-500">
                  <option>30 fps</option>
                  <option>60 fps</option>
                  <option>24 fps</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-2">Aspect Ratio</label>
                <div className="grid grid-cols-2 gap-2">
                  <button className="px-3 py-2 bg-cyan-500/20 border border-cyan-500/50 rounded-lg text-cyan-400 text-xs font-medium">
                    16:9
                  </button>
                  <button className="px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-slate-400 text-xs hover:border-cyan-500/50">
                    9:16
                  </button>
                  <button className="px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-slate-400 text-xs hover:border-cyan-500/50">
                    1:1
                  </button>
                  <button className="px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-slate-400 text-xs hover:border-cyan-500/50">
                    4:5
                  </button>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-700">
                <h3 className="text-xs font-semibold text-white mb-3">Recent Projects</h3>
                <div className="space-y-2">
                  {['Brand Intro Video', 'Product Showcase', 'Tutorial Series'].map((project, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-slate-800/30 border border-slate-700/50 rounded-lg hover:border-cyan-500/50 transition-all cursor-pointer"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Video className="w-3 h-3 text-cyan-400" />
                        <span className="text-xs font-medium text-white">{project}</span>
                      </div>
                      <p className="text-xs text-slate-500">2 days ago</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
