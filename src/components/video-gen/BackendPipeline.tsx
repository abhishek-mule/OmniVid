'use client';

import { motion } from 'framer-motion';
import { Server, Zap, Database, Film, ArrowRight } from 'lucide-react';

const pipelineSteps = [
  {
    icon: Server,
    label: 'FastAPI',
    description: 'Backend API',
    color: 'from-green-500 to-emerald-600'
  },
  {
    icon: Zap,
    label: 'Celery',
    description: 'Task Queue',
    color: 'from-yellow-500 to-orange-600'
  },
  {
    icon: Database,
    label: 'PostgreSQL',
    description: 'Database',
    color: 'from-blue-500 to-cyan-600'
  },
  {
    icon: Film,
    label: 'Remotion + FFmpeg',
    description: 'Video Rendering',
    color: 'from-purple-500 to-pink-600'
  }
];

export default function BackendPipeline() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative overflow-hidden rounded-2xl border border-border bg-card p-8"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent" />
      
      <div className="relative">
        <h2 className="text-xl font-semibold mb-6 text-center">
          Processing Pipeline
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {pipelineSteps.map((step, index) => (
            <div key={step.label} className="flex items-center">
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="flex-1"
              >
                <div className="relative group">
                  {/* Card */}
                  <div className="relative overflow-hidden rounded-xl border border-border bg-background p-4 transition-all duration-300 hover:shadow-lg hover:scale-105">
                    {/* Icon with gradient background */}
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${step.color} flex items-center justify-center mb-3 mx-auto`}>
                      <step.icon className="w-6 h-6 text-white" />
                    </div>

                    {/* Label */}
                    <h3 className="font-semibold text-center text-sm mb-1">
                      {step.label}
                    </h3>
                    <p className="text-xs text-muted-foreground text-center">
                      {step.description}
                    </p>

                    {/* Animated pulse effect */}
                    <motion.div
                      className={`absolute inset-0 bg-gradient-to-br ${step.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300 rounded-xl`}
                      animate={{
                        scale: [1, 1.05, 1],
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut"
                      }}
                    />
                  </div>

                  {/* Data flow animation */}
                  <motion.div
                    className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-primary"
                    animate={{
                      scale: [0, 1, 0],
                      opacity: [0, 1, 0],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      delay: index * 0.5,
                      ease: "easeInOut"
                    }}
                  />
                </div>
              </motion.div>

              {/* Arrow between steps */}
              {index < pipelineSteps.length - 1 && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 + 0.2 }}
                  className="hidden md:flex items-center justify-center px-2"
                >
                  <motion.div
                    animate={{
                      x: [0, 5, 0],
                      opacity: [0.3, 1, 0.3]
                    }}
                    transition={{
                      duration: 1.5,
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                  >
                    <ArrowRight className="w-5 h-5 text-muted-foreground" />
                  </motion.div>
                </motion.div>
              )}
            </div>
          ))}
        </div>

        {/* Status indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-6 flex items-center justify-center gap-2 text-sm text-muted-foreground"
        >
          <motion.div
            className="w-2 h-2 rounded-full bg-green-500"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.5, 1, 0.5]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
          <span>All systems operational</span>
        </motion.div>
      </div>
    </motion.div>
  );
}
