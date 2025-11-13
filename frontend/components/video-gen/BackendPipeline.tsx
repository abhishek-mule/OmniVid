'use client';

import { motion } from 'framer-motion';
import { Cpu, Zap, Video, Download } from 'lucide-react';

const steps = [
  { icon: Cpu, label: 'AI Processing', description: 'Analyzing your prompt' },
  { icon: Zap, label: 'Generation', description: 'Creating video content' },
  { icon: Video, label: 'Rendering', description: 'Finalizing video output' },
  { icon: Download, label: 'Complete', description: 'Ready for download' },
];

export default function BackendPipeline() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card rounded-lg border p-6 mb-8"
    >
      <h2 className="text-xl font-semibold mb-4">AI Video Generation Pipeline</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {steps.map((step, index) => (
          <div key={index} className="text-center">
            <div className="w-12 h-12 mx-auto mb-2 bg-primary/10 rounded-full flex items-center justify-center">
              <step.icon className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-medium text-sm">{step.label}</h3>
            <p className="text-xs text-muted-foreground">{step.description}</p>
          </div>
        ))}
      </div>
    </motion.div>
  );
}