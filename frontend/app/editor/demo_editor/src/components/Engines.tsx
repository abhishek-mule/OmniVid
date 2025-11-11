import { Film, Shapes, Code2, Box, Clapperboard } from 'lucide-react';

export default function Engines() {
  const engines = [
    {
      icon: Film,
      name: 'DaVinci Resolve',
      description: 'Professional cinematic editing and color grading',
      features: ['Cinematic Transitions', 'Color Correction', 'Timeline Editing'],
      gradient: 'from-red-500 to-orange-500'
    },
    {
      icon: Shapes,
      name: 'Manim',
      description: 'Mathematical animations and educational content',
      features: ['Math Visualizations', '2D Animations', 'Educational Graphics'],
      gradient: 'from-blue-500 to-cyan-500'
    },
    {
      icon: Code2,
      name: 'Remotion',
      description: 'React-based programmatic video generation',
      features: ['React Components', 'Motion Graphics', 'Data Visualization'],
      gradient: 'from-violet-500 to-purple-500'
    },
    {
      icon: Box,
      name: 'Blender',
      description: '3D modeling, animation, and procedural generation',
      features: ['3D Animation', 'Procedural Effects', 'Rendering'],
      gradient: 'from-orange-500 to-amber-500'
    },
    {
      icon: Clapperboard,
      name: 'FFmpeg',
      description: 'Video orchestration and final compilation',
      features: ['Format Conversion', 'Stream Processing', 'Compositing'],
      gradient: 'from-green-500 to-emerald-500'
    }
  ];

  return (
    <section className="relative py-24 px-4 bg-slate-900/30">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-500/10 border border-cyan-500/30 rounded-full text-cyan-400 text-sm mb-6">
            <Clapperboard className="w-4 h-4" />
            <span>Multi-Engine Architecture</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Powered by Industry Leaders
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Seamlessly orchestrates multiple professional rendering engines to create the perfect video
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {engines.map((engine, index) => (
            <div
              key={index}
              className="group relative bg-slate-900/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 transition-all duration-300 hover:border-cyan-500/50 hover:shadow-xl hover:shadow-cyan-500/10 hover:-translate-y-1"
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${engine.gradient} opacity-0 group-hover:opacity-5 rounded-2xl transition-opacity duration-300`}></div>

              <div className="relative">
                <div className={`inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br ${engine.gradient} mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                  <engine.icon className="w-7 h-7 text-white" strokeWidth={2} />
                </div>

                <h3 className="text-2xl font-semibold text-white mb-2">
                  {engine.name}
                </h3>

                <p className="text-slate-400 text-sm mb-4 leading-relaxed">
                  {engine.description}
                </p>

                <div className="space-y-2">
                  {engine.features.map((feature, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-slate-500 text-sm">
                      <div className="w-1.5 h-1.5 rounded-full bg-cyan-500"></div>
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <p className="text-slate-400 text-sm">
            All engines work together seamlessly through AI-powered orchestration
          </p>
        </div>
      </div>
    </section>
  );
}
