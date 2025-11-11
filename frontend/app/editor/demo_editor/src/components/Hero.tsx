import { Video, Sparkles, ChevronDown } from 'lucide-react';

export default function Hero() {
  const scrollToPrompt = () => {
    document.getElementById('prompt-section')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center px-4 overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-slate-900/50 to-transparent"></div>

      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-cyan-500/10 to-transparent rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-blue-500/10 to-transparent rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className="relative z-10 text-center max-w-5xl mx-auto">
        <div className="flex items-center justify-center mb-8 space-x-3">
          <div className="relative">
            <Video className="w-16 h-16 text-cyan-400" strokeWidth={1.5} />
            <Sparkles className="w-6 h-6 text-yellow-400 absolute -top-2 -right-2 animate-pulse" />
          </div>
        </div>

        <h1 className="text-7xl md:text-8xl font-bold mb-6 bg-gradient-to-r from-white via-cyan-100 to-blue-200 bg-clip-text text-transparent tracking-tight">
          OmniVid
        </h1>

        <p className="text-xl md:text-2xl text-slate-300 mb-4 font-light">
          AbhiAntrik AI
        </p>

        <div className="h-px w-32 mx-auto bg-gradient-to-r from-transparent via-cyan-500 to-transparent mb-8"></div>

        <p className="text-3xl md:text-4xl text-white mb-4 font-semibold leading-tight">
          Imagine. Compile. Create.
        </p>

        <p className="text-lg md:text-xl text-slate-400 mb-12 max-w-3xl mx-auto leading-relaxed">
          No timelines. No templates. Just type what you imagine, and let the AI compile it into motion.
        </p>

        <button
          onClick={scrollToPrompt}
          className="group relative inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full font-medium text-lg transition-all duration-300 hover:shadow-2xl hover:shadow-cyan-500/50 hover:scale-105"
        >
          <span>Start Creating</span>
          <Sparkles className="w-5 h-5 group-hover:rotate-180 transition-transform duration-500" />
        </button>
      </div>

      <button
        onClick={scrollToPrompt}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 text-slate-400 hover:text-cyan-400 transition-colors animate-bounce cursor-pointer"
        aria-label="Scroll to prompt"
      >
        <ChevronDown className="w-8 h-8" />
      </button>
    </div>
  );
}
