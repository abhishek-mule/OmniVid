import { MessageSquare, Code, Cog, Video, CheckCircle } from 'lucide-react';

export default function Workflow() {
  const steps = [
    {
      icon: MessageSquare,
      title: 'Prompt Parsing',
      description: 'AI analyzes your text using Mixtral-8x7B to understand creative intent',
      color: 'from-cyan-500 to-blue-500'
    },
    {
      icon: Code,
      title: 'Scene Generation',
      description: 'Converts your vision into structured scene logic and parameters',
      color: 'from-blue-500 to-violet-500'
    },
    {
      icon: Cog,
      title: 'Multi-Engine Compilation',
      description: 'Generates engine-specific code for Remotion, Blender, and more',
      color: 'from-violet-500 to-purple-500'
    },
    {
      icon: Video,
      title: 'Automated Rendering',
      description: 'Orchestrates multiple rendering engines to create your video',
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: CheckCircle,
      title: 'Final Export',
      description: 'Delivers a polished, production-ready video file',
      color: 'from-pink-500 to-rose-500'
    }
  ];

  return (
    <section className="relative py-24 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            How It Works
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            From imagination to reality in five automated steps
          </p>
        </div>

        <div className="relative">
          <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-500/20 via-violet-500/20 to-pink-500/20 hidden lg:block"></div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 relative">
            {steps.map((step, index) => (
              <div key={index} className="relative group">
                <div className="relative bg-slate-900/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 transition-all duration-300 hover:border-cyan-500/50 hover:shadow-xl hover:shadow-cyan-500/10 hover:-translate-y-2">
                  <div className={`absolute inset-0 bg-gradient-to-br ${step.color} opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity duration-300`}></div>

                  <div className="relative">
                    <div className={`inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br ${step.color} mb-4 shadow-lg`}>
                      <step.icon className="w-7 h-7 text-white" strokeWidth={2} />
                    </div>

                    <div className="absolute -top-2 -right-2 w-8 h-8 bg-slate-800 border border-slate-700 rounded-full flex items-center justify-center text-cyan-400 font-bold text-sm">
                      {index + 1}
                    </div>

                    <h3 className="text-xl font-semibold text-white mb-2">
                      {step.title}
                    </h3>

                    <p className="text-slate-400 text-sm leading-relaxed">
                      {step.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
