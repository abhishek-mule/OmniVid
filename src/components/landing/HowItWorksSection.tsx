'use client';

import { motion } from 'framer-motion';
import { MessageSquare, Sparkles, Download, CheckCircle } from 'lucide-react';

const steps = [
  {
    icon: MessageSquare,
    title: 'Describe Your Vision',
    description: 'Type what you want to create in natural language. Be as detailed or simple as you like.',
    color: 'text-violet-500',
    bgColor: 'bg-violet-500/10',
  },
  {
    icon: Sparkles,
    title: 'AI Works Its Magic',
    description: 'Watch as our AI generates your video in real-time with stage-by-stage progress updates.',
    color: 'text-fuchsia-500',
    bgColor: 'bg-fuchsia-500/10',
  },
  {
    icon: CheckCircle,
    title: 'Review & Customize',
    description: 'Fine-tune resolution, FPS, quality, and apply templates to perfect your creation.',
    color: 'text-pink-500',
    bgColor: 'bg-pink-500/10',
  },
  {
    icon: Download,
    title: 'Export & Share',
    description: 'Download in your preferred format and share your masterpiece with the world.',
    color: 'text-cyan-500',
    bgColor: 'bg-cyan-500/10',
  },
];

export function HowItWorksSection() {
  return (
    <section className="relative py-24 sm:py-32 bg-muted/30">
      <div className="container px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-20"
        >
          <h2 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
            <span className="bg-gradient-to-r from-violet-600 to-fuchsia-600 bg-clip-text text-transparent">
              How It Works
            </span>
          </h2>
          <p className="mt-6 text-xl text-muted-foreground max-w-3xl mx-auto">
            From idea to video in four simple steps
          </p>
        </motion.div>

        <div className="relative">
          {/* Connection line */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-violet-500 via-fuchsia-500 to-cyan-500 opacity-20" />

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-4">
            {steps.map((step, index) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.2, duration: 0.5 }}
                className="relative"
              >
                <div className="flex flex-col items-center text-center">
                  {/* Step number */}
                  <div className="relative mb-6">
                    <motion.div
                      whileHover={{ scale: 1.1, rotate: 5 }}
                      className={`w-20 h-20 rounded-2xl ${step.bgColor} flex items-center justify-center backdrop-blur-sm border border-border`}
                    >
                      <step.icon className={`w-10 h-10 ${step.color}`} />
                    </motion.div>
                    <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-gradient-to-br from-violet-600 to-fuchsia-600 flex items-center justify-center text-white font-bold text-sm">
                      {index + 1}
                    </div>
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {step.description}
                  </p>
                </div>

                {/* Connector arrow (desktop only) */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-10 -right-2 w-4 h-4 border-t-2 border-r-2 border-primary/30 rotate-45" />
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
