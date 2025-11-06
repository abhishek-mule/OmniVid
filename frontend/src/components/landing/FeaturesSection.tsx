'use client';

import { motion } from 'framer-motion';
import { Sparkles, Zap, BarChart2, Video, Clock, Users, Wand2, Palette } from 'lucide-react';

const features = [
  {
    icon: Wand2,
    title: 'Natural Language Input',
    description: 'Describe your vision in plain English. Our AI understands and creates.',
    gradient: 'from-violet-500 to-purple-500',
  },
  {
    icon: Zap,
    title: 'Lightning Fast',
    description: 'Generate professional videos in minutes, not hours. Real-time rendering.',
    gradient: 'from-amber-500 to-orange-500',
  },
  {
    icon: Palette,
    title: 'Stunning Templates',
    description: 'Choose from hundreds of professionally designed templates for any occasion.',
    gradient: 'from-pink-500 to-rose-500',
  },
  {
    icon: Video,
    title: '4K Quality',
    description: 'Export in up to 4K resolution with customizable FPS and quality settings.',
    gradient: 'from-cyan-500 to-blue-500',
  },
  {
    icon: BarChart2,
    title: 'Analytics Dashboard',
    description: 'Track performance, views, and engagement with detailed analytics.',
    gradient: 'from-green-500 to-emerald-500',
  },
  {
    icon: Users,
    title: 'Team Collaboration',
    description: 'Work together seamlessly with shared projects and real-time updates.',
    gradient: 'from-indigo-500 to-purple-500',
  },
];

export function FeaturesSection() {
  return (
    <section className="relative py-24 sm:py-32 overflow-hidden">
      <div className="container px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
            <span className="bg-gradient-to-r from-violet-600 to-fuchsia-600 bg-clip-text text-transparent">
              Everything You Need
            </span>
          </h2>
          <p className="mt-6 text-xl text-muted-foreground max-w-3xl mx-auto">
            Powerful features designed for creators who demand the best
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
              whileHover={{ y: -8, transition: { duration: 0.2 } }}
              className="relative group"
            >
              <div className="relative h-full p-8 rounded-2xl border border-border bg-card backdrop-blur-sm transition-all duration-300 hover:border-primary/50 hover:shadow-xl hover:shadow-primary/10">
                {/* Icon */}
                <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${feature.gradient} mb-6`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>

                {/* Content */}
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>

                {/* Hover glow */}
                <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300 -z-10`} />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
