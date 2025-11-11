import { Zap, Brain, Layers, Sparkles, Clock, Target } from 'lucide-react';

export default function Features() {
  const features = [
    {
      icon: Brain,
      title: 'AI-Driven Intelligence',
      description: 'Advanced LLMs understand your creative vision and translate it into actionable video instructions'
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Automated batch processing generates multiple videos in parallel, saving hours of manual work'
    },
    {
      icon: Layers,
      title: 'No Templates Required',
      description: 'Every video is uniquely generated from scratch based on your exact specifications'
    },
    {
      icon: Sparkles,
      title: 'Professional Quality',
      description: 'Industry-standard rendering engines ensure broadcast-ready output quality'
    },
    {
      icon: Clock,
      title: 'Instant Iteration',
      description: 'Refine and regenerate videos in seconds by simply adjusting your text prompt'
    },
    {
      icon: Target,
      title: 'Multi-Purpose',
      description: 'Perfect for brand intros, educational content, product showcases, and cinematic storytelling'
    }
  ];

  return (
    <section className="relative py-24 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Next-Era Video Creation
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Experience the future of video production with AI-powered automation
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group relative"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-blue-500/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

              <div className="relative h-full bg-slate-900/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 transition-all duration-300 hover:border-cyan-500/50">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                      <feature.icon className="w-6 h-6 text-white" strokeWidth={2} />
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-slate-400 text-sm leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-16 text-center">
          <div className="inline-block bg-slate-900/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 max-w-3xl">
            <p className="text-2xl text-white font-semibold mb-4">
              "Welcome to the next era of video."
            </p>
            <p className="text-slate-400 leading-relaxed">
              OmniVid eliminates the complexity of traditional video production.
              No timelines to manage, no effects to configure, no templates to customize.
              Just describe what you want, and let AI handle the rest.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
