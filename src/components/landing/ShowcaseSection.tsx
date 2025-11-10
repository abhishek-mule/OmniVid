'use client';

import { motion } from 'framer-motion';
import { Play } from 'lucide-react';

const showcaseVideos = [
  {
    title: 'Product Launch',
    category: 'Marketing',
    thumbnail: 'gradient-to-br from-violet-500 to-purple-600',
  },
  {
    title: 'Tutorial Series',
    category: 'Education',
    thumbnail: 'gradient-to-br from-cyan-500 to-blue-600',
  },
  {
    title: 'Social Media Ad',
    category: 'Advertising',
    thumbnail: 'gradient-to-br from-pink-500 to-rose-600',
  },
  {
    title: 'Event Highlights',
    category: 'Entertainment',
    thumbnail: 'gradient-to-br from-amber-500 to-orange-600',
  },
];

export function ShowcaseSection() {
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
              Creator Showcase
            </span>
          </h2>
          <p className="mt-6 text-xl text-muted-foreground max-w-3xl mx-auto">
            See what others are creating with OmniVid
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {showcaseVideos.map((video, index) => (
            <motion.div
              key={video.title}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
              whileHover={{ scale: 1.02 }}
              className="group relative cursor-pointer"
            >
              <div className="relative overflow-hidden rounded-2xl border border-border bg-card backdrop-blur-sm">
                <div className={`relative aspect-video bg-${video.thumbnail} flex items-center justify-center`}>
                  <motion.div
                    whileHover={{ scale: 1.1 }}
                    className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center border border-white/30 group-hover:bg-white/30 transition-all"
                  >
                    <Play className="w-8 h-8 text-white ml-1" />
                  </motion.div>
                </div>
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold">{video.title}</h3>
                      <p className="text-sm text-muted-foreground mt-1">{video.category}</p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
