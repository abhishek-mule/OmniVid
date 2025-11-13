'use client';

import { motion } from 'framer-motion';
import { Sparkles, Zap, Wand2, Video, Globe, Shield } from 'lucide-react';

const features = [
  {
    icon: Sparkles,
    title: 'AI Magic',
    description: 'Advanced AI models transform your text prompts into stunning visuals and narratives.',
    gradient: 'from-emerald-500 to-teal-500',
  },
  {
    icon: Zap,
    title: 'Lightning Fast',
    description: 'Generate professional videos in minutes, not hours. Optimized for speed and quality.',
    gradient: 'from-cyan-500 to-blue-500',
  },
  {
    icon: Wand2,
    title: 'Easy Editing',
    description: 'Intuitive controls let you fine-tune every aspect with just a few clicks.',
    gradient: 'from-teal-500 to-cyan-500',
  },
  {
    icon: Video,
    title: 'HD Quality',
    description: 'Export in 4K resolution with professional-grade rendering and effects.',
    gradient: 'from-emerald-500 to-cyan-500',
  },
  {
    icon: Globe,
    title: 'Multi-Language',
    description: 'Create videos in over 50 languages with natural voice synthesis.',
    gradient: 'from-blue-500 to-teal-500',
  },
  {
    icon: Shield,
    title: 'Secure & Private',
    description: 'Your content is encrypted and protected with enterprise-grade security.',
    gradient: 'from-cyan-500 to-emerald-500',
  },
];

export function Features() {
  return (
    <section id="features" className="relative py-24 md:py-32 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-emerald-500/5 to-transparent dark:via-emerald-500/10" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16 space-y-4"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 glass rounded-full">
            <Sparkles className="w-4 h-4 text-emerald-500" />
            <span className="text-sm font-medium">Powerful Features</span>
          </div>
          <h2 className="text-4xl sm:text-5xl md:text-6xl font-bold">
            Everything You Need to
            <br />
            <span className="text-gradient">Create Amazing Videos</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Packed with cutting-edge features designed to make video creation effortless and enjoyable.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ y: -8, scale: 1.02 }}
              className="group relative"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="relative glass-strong rounded-2xl p-8 h-full space-y-4 hover:border-emerald-500/30 transition-colors">
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-r ${feature.gradient} p-3 shadow-lg`}>
                  <feature.icon className="w-full h-full text-white" />
                </div>
                <h3 className="text-xl font-semibold">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
