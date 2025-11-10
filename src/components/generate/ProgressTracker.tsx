'use client';

import { motion } from 'framer-motion';
import { Progress } from '@/components/ui/progress';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

interface ProgressTrackerProps {
  progress: number;
  stage: string;
}

const stages = [
  { id: 'analyze', label: 'Analyzing Prompt', threshold: 0 },
  { id: 'script', label: 'Generating Script', threshold: 20 },
  { id: 'scenes', label: 'Creating Scenes', threshold: 40 },
  { id: 'render', label: 'Rendering Video', threshold: 60 },
  { id: 'finalize', label: 'Finalizing', threshold: 80 },
];

export function ProgressTracker({ progress, stage }: ProgressTrackerProps) {
  const getCurrentStageIndex = () => {
    return stages.findIndex(s => progress >= s.threshold && progress < (stages[stages.findIndex(st => st.id === s.id) + 1]?.threshold || 100));
  };

  const currentIndex = getCurrentStageIndex();

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">{stage}</span>
          <span className="text-sm font-semibold text-primary">{progress}%</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      <div className="space-y-3">
        {stages.map((s, index) => {
          const isComplete = progress > s.threshold && index < currentIndex;
          const isCurrent = index === currentIndex;
          const isPending = index > currentIndex;

          return (
            <motion.div
              key={s.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center gap-3"
            >
              <div className="flex-shrink-0">
                {isComplete && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  >
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                  </motion.div>
                )}
                {isCurrent && (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  >
                    <Loader2 className="w-5 h-5 text-primary" />
                  </motion.div>
                )}
                {isPending && (
                  <Circle className="w-5 h-5 text-muted-foreground/30" />
                )}
              </div>
              <span
                className={`text-sm ${
                  isComplete
                    ? 'text-foreground line-through opacity-60'
                    : isCurrent
                    ? 'text-primary font-medium'
                    : 'text-muted-foreground'
                }`}
              >
                {s.label}
              </span>
            </motion.div>
          );
        })}
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="p-3 rounded-lg bg-primary/5 border border-primary/20"
      >
        <p className="text-xs text-muted-foreground text-center">
          ✨ Your video is being crafted with AI magic...
        </p>
      </motion.div>
    </div>
  );
}
