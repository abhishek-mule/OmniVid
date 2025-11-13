'use client';

import { motion } from 'framer-motion';
import { Sparkles, Play } from 'lucide-react';

const videos = [
  {
    title: 'Product Launch',
    category: 'Marketing',
    gradient: 'from-rose-500 to-orange-500',
  },
  {
    title: 'Brand Story',
    category: 'Corporate',
    gradient: 'from-blue-500 to-cyan-500',
  },
  {
    title: 'Social Media',
    category: 'Content',
    gradient: 'from-emerald-500 to-teal-500',
  },
  {
    title: 'Tutorial',
    category: 'Education',
    gradient: 'from-purple-500 to-pink-500',
  },
  {
    title: 'Event Recap',
    category: 'Events',
    gradient: 'from-amber-500 to-yellow-500',
  },
  {
    title: 'Testimonial',
    category: 'Reviews',
    gradient: 'from-teal-500 to-emerald-500',
  },
];

export function Gallery() {
  return (
    <section id="gallery" className="relative py-24 md:py-32 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-teal-500/5 to-transparent dark:via-teal-500/10" />

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
            <span className="text-sm font-medium">Video Gallery</span>
          </div>
          <h2 className="text-4xl sm:text-5xl md:text-6xl font-bold">
            Discover What's
            <br />
            <span className="text-gradient">Possible</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Explore videos created by our community using OmniVid's AI technology.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
          {videos.map((video, index) => (
            <motion.div
              key={video.title}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ y: -8, scale: 1.02 }}
              className="group relative cursor-pointer"
            >
              <div className={`absolute inset-0 bg-gradient-to-r ${video.gradient} rounded-2xl blur-xl opacity-20 group-hover:opacity-40 transition-opacity`} />

              <div className="relative glass-strong rounded-2xl overflow-hidden">
                <div className={`aspect-video bg-gradient-to-br ${video.gradient} flex items-center justify-center relative overflow-hidden`}>
                  <div className="absolute inset-0 bg-black/40 group-hover:bg-black/20 transition-colors" />
                  <motion.div
                    whileHover={{ scale: 1.2 }}
                    className="relative z-10 w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center"
                  >
                    <Play className="w-8 h-8 text-white" fill="white" />
                  </motion.div>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold mb-1">{video.title}</h3>
                  <p className="text-sm text-muted-foreground">{video.category}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
