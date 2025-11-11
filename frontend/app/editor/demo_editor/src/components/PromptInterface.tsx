import { useState } from 'react';
import { Wand2, Loader2, Send } from 'lucide-react';

interface PromptInterfaceProps {
  isGenerating: boolean;
  setIsGenerating: (value: boolean) => void;
}

export default function PromptInterface({ isGenerating, setIsGenerating }: PromptInterfaceProps) {
  const [prompt, setPrompt] = useState('');

  const handleGenerate = () => {
    if (prompt.trim()) {
      setIsGenerating(true);
      setTimeout(() => {
        setIsGenerating(false);
      }, 3000);
    }
  };

  const examplePrompts = [
    "Create a cinematic brand intro with flying particles",
    "Animate a math formula explaining the Pythagorean theorem",
    "Generate a 3D product showcase with smooth camera movements",
    "Design an educational explainer about photosynthesis"
  ];

  return (
    <section id="prompt-section" className="relative py-24 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-500/10 border border-cyan-500/30 rounded-full text-cyan-400 text-sm mb-6">
            <Wand2 className="w-4 h-4" />
            <span>AI-Powered Video Generation</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Describe Your Vision
          </h2>
          <p className="text-slate-400 text-lg">
            Type your idea, and watch as AI transforms it into a professional video
          </p>
        </div>

        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-2xl blur-xl"></div>

          <div className="relative bg-slate-900/80 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 shadow-2xl">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the video you want to create... e.g., 'Create a futuristic tech brand intro with neon lights and smooth transitions'"
              className="w-full h-40 bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 resize-none focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all"
              disabled={isGenerating}
            />

            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-slate-500">
                {prompt.length} characters
              </div>

              <button
                onClick={handleGenerate}
                disabled={!prompt.trim() || isGenerating}
                className="group relative inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl font-medium transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/50 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <span>Generate Video</span>
                    <Send className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        <div className="mt-8">
          <p className="text-slate-500 text-sm mb-3 text-center">Try these examples:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {examplePrompts.map((example, index) => (
              <button
                key={index}
                onClick={() => setPrompt(example)}
                className="text-left px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-lg text-slate-300 text-sm hover:border-cyan-500/50 hover:bg-slate-800 transition-all"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
